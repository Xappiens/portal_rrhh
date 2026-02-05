import frappe
from frappe import _
from frappe.utils import flt, getdate, today, date_diff, add_days
from hrms.hr import utils as hrms_utils

@frappe.whitelist()
def get_dashboard_data(employee=None):
    """
    Get aggregated dashboard data for the employee:
    - Total Allocated Days/Hours
    - Total Consumed Days/Hours
    - Balance (Remaining)
    - Available Leave Types
    """
    if not employee:
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
    if not employee:
        return {"error": "Employee not found"}

    # Get all active allocations
    allocations = frappe.get_all(
        "Spanish Leave Allocation",
        filters={
            "employee": employee,
            "docstatus": 1,
            # We might want to filter by valid dates, but active allocations typically means
            # current contracts. For simplicity, we take all active ones or filter by year/validity if needed.
            # Assuming 'active' means not expired or current year.
            # For now, let's fetch all providing positive balance or current validity.
        },
        fields=["days_allocated", "hours_allocated", "days_consumed", "hours_consumed", "days_remaining", "hours_remaining", "leave_type"]
    )

    # Aggregate Data
    dashboard = {
        "total_days_allocated": 0.0,
        "total_days_consumed": 0.0,
        "total_days_remaining": 0.0,
        "total_hours_allocated": 0.0,
        "total_hours_consumed": 0.0,
        "total_hours_remaining": 0.0,
        "leave_types_config": {}
    }

    # Fetch Leave Type configs to know if they allow hours, etc
    leave_types = frappe.get_all("Spanish Leave Type", fields=["name", "leave_type_name", "allow_hours_request", "hours_per_day", "allow_negative_balance"])
    lt_map = {lt.name: lt for lt in leave_types}

    for alloc in allocations:
        dashboard["total_days_allocated"] += flt(alloc.days_allocated)
        dashboard["total_days_consumed"] += flt(alloc.days_consumed)
        dashboard["total_days_remaining"] += flt(alloc.days_remaining)
        
        dashboard["total_hours_allocated"] += flt(alloc.hours_allocated)
        dashboard["total_hours_consumed"] += flt(alloc.hours_consumed)
        dashboard["total_hours_remaining"] += flt(alloc.hours_remaining)

    # Calculate Pending Approval (User's own requests)
    pending_apps = frappe.get_all(
        "Spanish Leave Application",
        filters={"employee": employee, "status": "Abierta"},
        fields=["total_days", "total_hours", "request_type"]
    )
    
    dashboard["total_days_pending"] = sum(flt(app.total_days) for app in pending_apps if app.request_type == "Por Días")
    dashboard["total_hours_pending"] = sum(flt(app.total_hours) for app in pending_apps if app.request_type != "Por Días")

    dashboard["leave_types_config"] = [lt for lt in leave_types]
    
    # Check if user is an approver
    # We check if this user is set as leave_approver for anyone active
    team_members_count = frappe.db.count("Employee", {"leave_approver": frappe.session.user, "status": "Active"})
    dashboard["is_approver"] = team_members_count > 0
    dashboard["team_members_count"] = team_members_count
    
    # Check user roles
    roles = frappe.get_roles(frappe.session.user)
    dashboard["has_validar_hc_role"] = "Validar HC" in roles
    
    if dashboard["is_approver"]:
        dashboard["pending_team_requests"] = frappe.db.count("Spanish Leave Application", {
            "leave_approver": frappe.session.user,
            "status": "Abierta"
        })
    else:
        dashboard["pending_team_requests"] = 0

    return dashboard

@frappe.whitelist()
def get_my_leaves(employee=None):
    """
    Get all leave applications for the employee
    """
    if not employee:
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
    if not employee:
        return []

    leaves = frappe.get_all(
        "Spanish Leave Application",
        filters={"employee": employee},
        fields=["name", "leave_type", "status", "from_date", "to_date", "total_days", "request_type", "total_hours", "description", "request_date", "leave_approver_name"],
        order_by="modified desc"
    )
    
    # Fetch attachments (múltiples por solicitud)
    if leaves:
        leave_names = [l.name for l in leaves]
        files = frappe.get_all("File", filters={
            "attached_to_doctype": "Spanish Leave Application",
            "attached_to_name": ["in", leave_names]
        }, fields=["name", "file_url", "file_name", "attached_to_name"])
        
        # Agrupar archivos por solicitud
        file_map = {}
        for f in files:
            if f.attached_to_name not in file_map:
                file_map[f.attached_to_name] = []
            file_map[f.attached_to_name].append({
                "name": f.name,
                "file_url": f.file_url,
                "file_name": f.file_name
            })
        
        for l in leaves:
            l["attachments"] = file_map.get(l.name, [])
            # Mantener compatibilidad con código anterior
            l["attachment"] = l["attachments"][0]["file_url"] if l["attachments"] else None

    return leaves

@frappe.whitelist()
def get_team_requests(status=None, employee=None, leave_type=None, location=None, only_my_team=None):
    """
    Get requests for employees reporting to the current user.
    status: 'Abierta' (Pending), 'History' (Approved/Rejected/Cancelled), or None (All)
    employee: Filter by specific employee
    leave_type: Filter by specific leave type
    location: Filter by employee's custom_centro (Room)
    only_my_team: If True and user has "Validar HC" role, filter by leave_approver = current user
    """
    filters = {}
    
    # Permission Filter
    roles = frappe.get_roles(frappe.session.user)
    if frappe.session.user != "Administrator":
        if "Responsable Departamento" in roles:
            filters["leave_approver"] = frappe.session.user
        elif "Validador HR" not in roles and "Validar HC" not in roles:
            filters["leave_approver"] = frappe.session.user
        elif "Validar HC" in roles and only_my_team:
            # Si tiene rol "Validar HC" y activó el filtro "Solo mi equipo", filtrar por leave_approver
            filters["leave_approver"] = frappe.session.user

    # Status Filter
    if status == 'Abierta' or status == 'Pending':
        filters["status"] = "Abierta"
    elif status == 'History':
        filters["status"] = ["in", ["Aprobada", "Rechazada", "Cancelada"]]
    elif status:
        filters["status"] = status
    
    # Employee Filter
    if employee:
        filters["employee"] = employee
        
    # Leave Type Filter
    if leave_type:
        filters["leave_type"] = leave_type

    # Location Filter (via Employee)
    if location:
        # Fetch employees in this location
        employees_in_location = frappe.get_all("Employee", filters={"custom_centro": location}, pluck="name")
        if not employees_in_location:
            return [] # No employees in this location
        
        # Merge with existing employee filter if present
        if filters.get("employee"):
            if filters["employee"] not in employees_in_location:
                return []
        else:
             filters["employee"] = ["in", employees_in_location]

    requests = frappe.get_all(
        "Spanish Leave Application",
        filters=filters,
        fields=["name", "employee", "employee_name", "leave_type", "status", "from_date", "to_date", "total_days", "request_type", "total_hours", "description", "request_date", "creation", "modified"],
        order_by="creation desc"
    )

    # Fetch attachments (múltiples por solicitud)
    if requests:
        request_names = [r.name for r in requests]
        files = frappe.get_all("File", filters={
            "attached_to_doctype": "Spanish Leave Application",
            "attached_to_name": ["in", request_names]
        }, fields=["name", "file_url", "file_name", "attached_to_name"])
        
        # Agrupar archivos por solicitud
        file_map = {}
        for f in files:
            if f.attached_to_name not in file_map:
                file_map[f.attached_to_name] = []
            file_map[f.attached_to_name].append({
                "name": f.name,
                "file_url": f.file_url,
                "file_name": f.file_name
            })
        
        for r in requests:
            r["attachments"] = file_map.get(r.name, [])
            # Mantener compatibilidad con código anterior
            r["attachment"] = r["attachments"][0]["file_url"] if r["attachments"] else None

    return requests

@frappe.whitelist()
def get_team_leaves(month_start=None, month_end=None, employee=None, leave_type=None, location=None):
    """
    Get approved and pending leaves for the team calendar/gantt
    Includes both 'Aprobada' and 'Abierta' (pending) requests for planning
    """
    filters = {
        "status": ["in", ["Aprobada", "Abierta"]], 
    }
    
    roles = frappe.get_roles(frappe.session.user)
    if frappe.session.user != "Administrator":
        if "Responsable Departamento" in roles:
            filters["leave_approver"] = frappe.session.user
        elif "Validador HR" not in roles and "Validar HC" not in roles:
            filters["leave_approver"] = frappe.session.user
    
    if month_start and month_end:
        filters["to_date"] = [">=", month_start]
        filters["from_date"] = ["<=", month_end]
        
    if employee:
        filters["employee"] = employee

    if leave_type:
        filters["leave_type"] = leave_type

    if location:
        employees_in_location = frappe.get_all("Employee", filters={"custom_centro": location}, pluck="name")
        if not employees_in_location:
            return []
            
        if filters.get("employee"):
             if filters["employee"] not in employees_in_location:
                 return []
        else:
             filters["employee"] = ["in", employees_in_location]
        
    leaves = frappe.get_all(
        "Spanish Leave Application",
        filters=filters,
        fields=["name", "employee_name", "from_date", "to_date", "leave_type", "employee", "status", "description", "request_type", "request_date", "total_hours"],
        order_by="from_date asc"
    )

    # Fetch attachments (múltiples por solicitud)
    if leaves:
        leave_names = [l.name for l in leaves]
        files = frappe.get_all("File", filters={
            "attached_to_doctype": "Spanish Leave Application",
            "attached_to_name": ["in", leave_names]
        }, fields=["name", "file_url", "file_name", "attached_to_name"])
        
        # Agrupar archivos por solicitud
        file_map = {}
        for f in files:
            if f.attached_to_name not in file_map:
                file_map[f.attached_to_name] = []
            file_map[f.attached_to_name].append({
                "name": f.name,
                "file_url": f.file_url,
                "file_name": f.file_name
            })
        
        for l in leaves:
            l["attachments"] = file_map.get(l.name, [])
            # Mantener compatibilidad con código anterior
            l["attachment"] = l["attachments"][0]["file_url"] if l["attachments"] else None

    return leaves

@frappe.whitelist()
def create_leave_application(data):
    """
    Create a new Spanish Leave Application
    data: json string or dict
    """
    import json
    if isinstance(data, str):
        data = json.loads(data)

    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        frappe.throw(_("No se encontró un empleado asociado a tu usuario."))

    # Get approver from Employee master
    approver = frappe.db.get_value("Employee", employee, "leave_approver") # Or however it's defined in your system
    if not approver:
        # Fallback or error? Let's check reports_to
        reports_to = frappe.db.get_value("Employee", employee, "reports_to")
        if reports_to:
             approver = frappe.db.get_value("Employee", reports_to, "user_id")
    
    if not approver:
         frappe.throw(_("No tienes un aprobador de vacaciones asignado. Contacta a RRHH."))

    doc = frappe.new_doc("Spanish Leave Application")
    doc.employee = employee
    doc.item_type = data.get("leave_type") # Fieldname mismatch fix: json has leave_type
    doc.leave_type = data.get("leave_type")
    doc.request_type = data.get("request_type", "Por Días")
    doc.description = data.get("description")
    doc.leave_approver = approver
    
    if doc.request_type == "Por Días":
        doc.from_date = getdate(data.get("from_date"))
        doc.to_date = getdate(data.get("to_date"))
    else:
        doc.request_date = getdate(data.get("request_date")) # Single date for hours?
        # Logic says request_date is usually the day of the hours
        doc.total_hours = flt(data.get("hours", 0))
    
    doc.insert(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def process_request(name, action):
    """
    Approve or Reject a request
    action: 'approve' | 'reject'
    """
    doc = frappe.get_doc("Spanish Leave Application", name)
    
    # Validate permissions (approver)
    if doc.leave_approver != frappe.session.user and frappe.session.user != "Administrator":
        frappe.throw(_("No tienes permiso para procesar esta solicitud."))
        
    if action == "approve":
        doc.status = "Aprobada"
        # Usar ignore_permissions porque el aprobador ya fue validado arriba
        # y necesita poder actualizar asignaciones automáticamente
        doc.flags.ignore_permissions = True
        doc.submit()
    elif action == "reject":
        doc.status = "Rechazada"
        doc.save()
    elif action == "cancel":
        if doc.status == "Aprobada":
            # Usar ignore_permissions para poder cancelar y revertir asignaciones
            doc.flags.ignore_permissions = True
            doc.cancel()
        else:
             frappe.throw(_("Solo se pueden cancelar solicitudes aprobadas."))
        
    return doc.status

@frappe.whitelist()
def get_leave_form_context(employee=None):
    """
    Get context for the leave request form:
    1. Approver info
    2. Active Allocations (Balances) - From Spanish Leave Allocations
    3. Holiday list for current and next year
    """
    if not employee:
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
    if not employee:
        return {"error": "Employee not found"}

    context = {
        "approver": None,
        "allocations": [],
        "holidays": []
    }

    # 1. Approver
    approver_id = frappe.db.get_value("Employee", employee, "leave_approver")
    if not approver_id:
        reports_to = frappe.db.get_value("Employee", employee, "reports_to")
        if reports_to:
            approver_id = frappe.db.get_value("Employee", reports_to, "user_id")
    
    if approver_id:
        context["approver"] = {
            "user": approver_id,
            "name": frappe.db.get_value("User", approver_id, "full_name") or approver_id
        }

    today_date = today()
    
    # 2. Allocations (Spanish Leave Allocation)
    # Fetch active allocations (submitted and not expired/cancelled logic handled by docstatus=1)
    # We might want to filter by contract dates or just show all active?
    # Usually active ones have docstatus=1.
    allocations = frappe.get_all(
        "Spanish Leave Allocation",
        filters={
            "employee": employee,
            "docstatus": 1
        },
        fields=["name", "leave_type", "days_remaining", "hours_remaining", "contract_start_date", "contract_end_date"],
        order_by="contract_start_date desc"
    )
    
    # 3. Holidays
    # Get holiday list name for display
    holiday_list_name = frappe.db.get_value("Employee", employee, "holiday_list")
    
    holidays = []
    if not holiday_list_name:
         # Try to get default company holiday list if employee has none
         company = frappe.db.get_value("Employee", employee, "company")
         if company:
             holiday_list_name = frappe.db.get_value("Company", company, "default_holiday_list")
    
    if holiday_list_name:
        # Fetch holidays for huge range to be safe (current year and next)
        start_year = getdate(today_date).year
        end_date = f"{start_year + 1}-12-31"
        start_date = f"{start_year}-01-01"
        
        holidays_list = hrms_utils.get_holidays_for_employee(employee, start_date, end_date)
        # convert dates to strings
        holidays = [str(h.get("holiday_date")) for h in holidays_list]

    # Get Rooms (Centers) for filters
    rooms = frappe.get_all("Room", fields=["name", "room_name"], order_by="room_name asc")

    return {
        "approver": context.get("approver"),
        "allocations": allocations,
        "holiday_list_name": holiday_list_name, # Renamed key to match frontend expectation if any
        "holidays": holidays,
        "rooms": rooms
    }

@frappe.whitelist()
def calculate_effective_days(from_date, to_date):
    """
    Calculate effective working days between two dates for the current user/employee.
    """
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return 0
        
    from spanish_leave.spanish_leave.doctype.spanish_leave_application.spanish_leave_application import count_working_days_excluding_holidays
    
    days = count_working_days_excluding_holidays(
        employee,
        getdate(from_date),
        getdate(to_date)
    )
    
    return days

@frappe.whitelist()
def get_my_team_members():
    """
    Get list of employees where the current user is the leave approver.
    Or employees that report to this user (if no explicit leave approver set on them? 
    Consistency: get_dashboard_data uses leave_approver only).
    Let's stick to leave_approver strict match for now as per system design.
    """
    filters = {
        "status": "Active"
    }

    roles = frappe.get_roles(frappe.session.user)
    if frappe.session.user != "Administrator":
        if "Responsable Departamento" in roles:
            filters["leave_approver"] = frappe.session.user
        elif "Validador HR" not in roles and "Validar HC" not in roles:
            filters["leave_approver"] = frappe.session.user

    employees = frappe.get_all("Employee", 
        filters=filters,
        fields=["name", "employee_name", "custom_centro"],
        order_by="employee_name asc"
    )
    return employees

@frappe.whitelist()
def delete_attachment(file_name, docname):
    """
    Eliminar un archivo adjunto de una solicitud de vacaciones.
    file_name: nombre del File document (ej: "d3f4a5b6c7")
    docname: nombre del Spanish Leave Application
    """
    # Verificar que el archivo pertenece al documento especificado
    file_doc = frappe.get_doc("File", file_name)
    
    if file_doc.attached_to_doctype != "Spanish Leave Application":
        frappe.throw(_("El archivo no pertenece a una solicitud de vacaciones."))
    
    if file_doc.attached_to_name != docname:
        frappe.throw(_("El archivo no pertenece a esta solicitud."))
    
    # Verificar que el usuario tiene permiso (es el dueño de la solicitud)
    leave_doc = frappe.get_doc("Spanish Leave Application", docname)
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    
    if leave_doc.employee != employee and frappe.session.user != "Administrator":
        # También permitir si es el aprobador
        if leave_doc.leave_approver != frappe.session.user:
            frappe.throw(_("No tienes permiso para eliminar este archivo."))
    
    # Eliminar el archivo
    frappe.delete_doc("File", file_name, ignore_permissions=True)
    
    return {"success": True, "message": "Archivo eliminado correctamente"}
