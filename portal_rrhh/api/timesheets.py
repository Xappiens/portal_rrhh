import frappe
from frappe import _
from frappe.utils import getdate, today, add_days, get_first_day, get_last_day, flt
from datetime import datetime, timedelta
import json

def get_employee():
    """Get the employee record for the current user. Returns None if not found."""
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, ["name", "custom_centro"], as_dict=True)
    return employee  # Retorna None si no encuentra empleado, sin lanzar excepción

@frappe.whitelist()
def get_user_settings():
    """Get settings for the current user/employee."""
    employee = get_employee()
    
    # Si no hay empleado, retornar configuración vacía
    if not employee:
        return {
            "employee_name": None,
            "default_sede": None,
            "default_sede_name": None
        }
    
    default_sede = employee.get("custom_centro")
    default_sede_name = ""
    
    if default_sede:
        default_sede_name = frappe.db.get_value("Room", default_sede, "room_name")

    return {
        "employee_name": employee["name"],
        "default_sede": default_sede,
        "default_sede_name": default_sede_name
    }

@frappe.whitelist()
def get_timesheets(start_date=None, end_date=None, start=0, page_length=20):
    """Get list of timesheets for the current employee."""
    employee = get_employee()
    
    # Si no hay empleado, retornar lista vacía
    if not employee:
        return []
    
    filters = {"employee": employee["name"]}
    
    # Default to last 2 months if no date range is provided
    if not start_date and not end_date:
        start_date = add_days(today(), -60)
        
    if start_date:
        filters["start_date"] = [">=", start_date]
    if end_date:
        filters["end_date"] = ["<=", end_date]

    timesheets = frappe.get_list(
        "Timesheet",
        fields=["name", "start_date", "end_date", "status", "total_hours", "workflow_state"],
        filters=filters,
        order_by="start_date desc",
        start=start,
        page_length=page_length
    )
    return timesheets

@frappe.whitelist()
def get_timesheet_details(name):
    """Get full details of a timesheet."""
    try:
        timesheet = frappe.get_doc("Timesheet", name)
        
        # Verify permission (own timesheet)
        employee = get_employee()
        if not employee:
            frappe.throw(_("No se encontró un registro de empleado asociado a tu usuario."), frappe.PermissionError)
        
        if timesheet.employee != employee["name"]:
            frappe.throw(_("No tienes permiso para ver este documento."), frappe.PermissionError)

        return timesheet.as_dict()
    except frappe.DoesNotExistError:
        frappe.throw(_("Timesheet no encontrado."), frappe.DoesNotExistError)

@frappe.whitelist()
def save_timesheet(data):
    """Create or update a timesheet."""
    if isinstance(data, str):
        data = json.loads(data)
    
    employee = get_employee()
    if not employee:
        frappe.throw(_("No se encontró un registro de empleado asociado a tu usuario."))
    
    # Check if we are updating or creating
    name = data.get("name")
    if name:
        doc = frappe.get_doc("Timesheet", name)
        if doc.employee != employee["name"]:
            frappe.throw(_("No puedes modificar este documento."), frappe.PermissionError)
        if doc.docstatus == 1:
            frappe.throw(_("No se puede editar un timesheet ya validado."))
    else:
        # Create new Timesheet
        doc = frappe.new_doc("Timesheet")
        doc.employee = employee["name"]
        doc.start_date = data.get("start_date")
        doc.end_date = data.get("end_date")
        
    # VALIDATION: Check for overlapping timesheets
    # We want to check if there is ANY other timesheet for this employee that overlaps.
    # Overlap logic: (StartA <= EndB) and (EndA >= StartB)
    # We exclude the current doc.name if it exists (update scenario)
    
    start_date = doc.start_date or data.get("start_date")
    end_date = doc.end_date or data.get("end_date")
    
    if start_date and end_date:
        filters = {
            "employee": employee["name"],
            "name": ["!=", doc.name] if doc.name else ["is", "set"], # Only exclude if we have a name (update)
            "docstatus": ["<", 2], # Exclude cancelled
            "start_date": ["<=", end_date],
            "end_date": [">=", start_date]
        }
        
        # If new doc, name is None, so filters["name"] check might be weird.
        # Better construction:
        query_filters = [
            ["Timesheet", "employee", "=", employee["name"]],
            ["Timesheet", "docstatus", "<", 2],
            ["Timesheet", "start_date", "<=", end_date],
            ["Timesheet", "end_date", ">=", start_date]
        ]
        
        if doc.name:
             query_filters.append(["Timesheet", "name", "!=", doc.name])
             
        existing = frappe.get_all("Timesheet", filters=query_filters, limit=1)
        
        if existing:
            frappe.throw(_("Ya existe un registro de horas para este periodo (Semana: {0})").format(start_date), frappe.ValidationError)

    # Update basic fields (redundant for new doc but safe)
    if "start_date" in data:
        doc.start_date = data["start_date"]
    if "end_date" in data:
         doc.end_date = data["end_date"]

    # Update Child Table: custom_sede_time_logs
    if "logs" in data:
        # We replace all logs or merge? Usually safer to clear and re-add for full sync in SPA
        # BUT we must be careful with existing IDs if we want to update.
        # Impl: Clear and re-add is easiest for "save state".
        # Calculate total hours manually since we skip validate()
        total_hours = 0.0
        
        doc.set("custom_sede_time_logs", [])
        doc.set("time_logs", []) 
        
        # Get a default activity type just in case, or leave blank if we ignore mandatory
        default_activity = frappe.db.get_value("Activity Type", {"name": "Horas de creación de contenidos/materiales"}, "name")
        if not default_activity:
             default_activity = frappe.db.get_value("Activity Type", {}, "name")
        
        for log in data["logs"]:
            # Custom Log
            row = doc.append("custom_sede_time_logs", {})
            row.date = log.get("date")
            row.hours = flt(log.get("hours"))
            row.sede = log.get("sede")
            row.plan = log.get("plan")
            row.course = log.get("course")
            row.expediente = log.get("expediente")
            
            total_hours += row.hours
            
            # Standard Log
            # We populate this ONLY to satisfy the "Time Logs" table presence if needed, 
            # and for potential future reporting, but we bypass validation.
            # User explicitly requested NO invented hours and NO activity requirement.
            std_row = doc.append("time_logs", {})
            std_row.activity_type = default_activity 
            std_row.hours = row.hours
            std_row.description = "Registro automático desde Portal RRHH"
            std_row.date = row.date
            
            # Populate mandatory time fields to satisfy ERPNext validation
            # We assume a standard start time of 09:00:00
            if row.hours > 0:
                from_time_str = f"{row.date} 09:00:00"
                # Add hours to start time
                start_dt = datetime.strptime(from_time_str, "%Y-%m-%d %H:%M:%S")
                end_dt = start_dt + timedelta(hours=row.hours)
                
                std_row.from_time = start_dt
                std_row.to_time = end_dt
            
        doc.total_hours = total_hours
        
    # Flags to bypass standard validations (Overlap, From/To Time mandatory, etc)
    doc.flags.ignore_validate = True
    doc.flags.ignore_mandatory = True
            
    doc.save()
    return doc.as_dict()

@frappe.whitelist()
def submit_timesheet(name):
    """Submit the timesheet."""
    doc = frappe.get_doc("Timesheet", name)
    employee = get_employee()
    
    if not employee:
        frappe.throw(_("No se encontró un registro de empleado asociado a tu usuario."), frappe.PermissionError)
    
    if doc.employee != employee["name"]:
        frappe.throw(_("No tienes permiso para validar este documento."), frappe.PermissionError)
        
    if doc.docstatus == 1:
        return doc.as_dict()

    doc.status = "Submitted"
    doc.flags.ignore_validate = True
    doc.flags.ignore_mandatory = True
    doc.submit()
    return doc.as_dict()

@frappe.whitelist()
def delete_timesheet(name):
    """Delete a timesheet (only if Draft)."""
    doc = frappe.get_doc("Timesheet", name)
    employee = get_employee()
    
    if not employee:
        frappe.throw(_("No se encontró un registro de empleado asociado a tu usuario."), frappe.PermissionError)
    
    if doc.employee != employee["name"]:
        frappe.throw(_("No tienes permiso para eliminar este documento."), frappe.PermissionError)
        
    if doc.docstatus != 0:
        frappe.throw(_("Solo se pueden eliminar borradores."))
        
    frappe.delete_doc("Timesheet", name)
    return True

@frappe.whitelist()
def get_sedes():
    """Get list of active Sedes (Rooms)."""
    # Assuming 'Room' doctype is used for Sedes as per context
    return frappe.get_all("Room", fields=["name", "room_name"], filters={"custom_de_baja": 0}, order_by="room_name")

@frappe.whitelist()
def get_planes(txt=None, limit=50):
    """Get list of active Planes Formativos."""
    filters = {}
    
    or_filters = None
    if txt:
        or_filters = {
            "name": ["like", f"%{txt}%"],
            "n_plan_formativo": ["like", f"%{txt}%"],
            "custom_descripción_del_plan": ["like", f"%{txt}%"],
            "plan_formativo": ["like", f"%{txt}%"] 
        }
        
    return frappe.get_all("Planes Formativos", 
        fields=["name", "custom_descripción_del_plan", "n_plan_formativo", "plan_formativo", "custom_numero_plan_formativo"], 
        filters=filters, 
        or_filters=or_filters,
        order_by="name desc", 
        limit_page_length=limit
    )

@frappe.whitelist()
def get_courses(txt=None, program=None, plan=None, limit=50):
    """Get list of active Courses with optional search and filters."""
    filters = {}
    or_filters = None
    
    # We want to filter by program/plan strictly if provided
    if program:
        filters["expediente"] = program
    if plan and not program: 
        filters["custom_plan"] = plan

    if txt:
        or_filters = {
            "name": ["like", f"%{txt}%"],
            "custom_display_identifier": ["like", f"%{txt}%"],
            "course_name": ["like", f"%{txt}%"]
        }
    
    return frappe.get_all("Course", 
        fields=["name", "course_name", "custom_display_identifier", "expediente", "custom_plan"], 
        filters=filters, 
        or_filters=or_filters,
        order_by="custom_display_identifier", 
        limit_page_length=limit
    )

@frappe.whitelist()
def get_programs(txt=None, plan=None, limit=50):
    """Get list of active Programs (Expedientes) with optional search and plan filter."""
    filters = {}
    or_filters = None
    
    if plan:
        filters["custom_plan"] = plan
        
    if txt:
        or_filters = {
            "name": ["like", f"%{txt}%"],
            "custom_num_de_expediente": ["like", f"%{txt}%"],
            "program_name": ["like", f"%{txt}%"]
        }
        
    return frappe.get_all("Program", 
        fields=["name", "program_name", "custom_num_de_expediente", "custom_plan"], 
        filters=filters, 
        or_filters=or_filters, 
        order_by="custom_num_de_expediente", 
        limit_page_length=limit
    )
