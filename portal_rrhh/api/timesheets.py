import frappe
from frappe import _
from frappe.utils import getdate, today, add_days, get_first_day, get_last_day, flt
import json

def get_employee():
    """Get the employee record for the current user."""
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, ["name", "custom_centro"], as_dict=True)
    if not employee:
        frappe.throw(_("No se encontró un registro de empleado asociado a tu usuario."))
    return employee

@frappe.whitelist()
def get_user_settings():
    """Get settings for the current user/employee."""
    employee = get_employee()
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
    
    # Check if we are updating or creating
    name = data.get("name")
    if name:
        doc = frappe.get_doc("Timesheet", name)
        if doc.employee != employee["name"]:
            frappe.throw(_("No puedes modificar este documento."), frappe.PermissionError)
        if doc.docstatus == 1:
            frappe.throw(_("No se puede editar un timesheet ya validado."))
    else:
        doc = frappe.new_doc("Timesheet")
        doc.employee = employee["name"]
        doc.start_date = data.get("start_date")
        doc.end_date = data.get("end_date") # Usually calculated, but can be passed. 
        # Ideally we should set end_date based on start_date (weekly) if not provided?
        # Let's assume frontend sends correct dates or we calculate.
        if not doc.end_date and doc.start_date:
             # Default to 1 week if not set? But usually timesheet logic is strict.
             pass

    # Update basic fields
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
            row.course = log.get("course")
            row.expediente = log.get("expediente")
            
            total_hours += row.hours
            
            # Standard Log
            # We populate this ONLY to satisfy the "Time Logs" table presence if needed, 
            # and for potential future reporting, but we bypass validation.
            # User explicitly requested NO invented hours and NO activity requirement.
            std_row = doc.append("time_logs", {})
            std_row.activity_type = default_activity # Keep default to be safe against some strict reports, but can be blank with ignore_mandatory
            std_row.hours = row.hours
            std_row.description = "Registro automático desde Portal RRHH"
            std_row.date = row.date
            # No from_time / to_time populated
            
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
    
    if doc.employee != employee["name"]:
        frappe.throw(_("No tienes permiso para validar este documento."), frappe.PermissionError)
        
    if doc.docstatus == 1:
        return doc.as_dict()

    doc.submit()
    return doc.as_dict()

@frappe.whitelist()
def get_sedes():
    """Get list of active Sedes (Rooms)."""
    # Assuming 'Room' doctype is used for Sedes as per context
    return frappe.get_all("Room", fields=["name", "room_name"], filters={"custom_de_baja": 0}, order_by="room_name")

@frappe.whitelist()
def get_courses(txt=None, program=None):
    """Get list of active Courses with optional search and program filter."""
    filters = {}
    if txt:
        filters["custom_display_identifier"] = ["like", f"%{txt}%"]
    if program:
        # Link field identified as 'expediente'
        filters["expediente"] = program
    
    return frappe.get_all("Course", fields=["name", "course_name", "custom_display_identifier"], filters=filters, order_by="custom_display_identifier", limit_page_length=20)

@frappe.whitelist()
def get_programs(txt=None):
    """Get list of active Programs (Expedientes) with optional search."""
    filters = {}
    if txt:
        filters["custom_num_de_expediente"] = ["like", f"%{txt}%"]
        
    return frappe.get_all("Program", fields=["name", "program_name", "custom_num_de_expediente"], filters=filters, order_by="custom_num_de_expediente", limit_page_length=20)
