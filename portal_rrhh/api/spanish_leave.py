import frappe
from frappe import _
from frappe.utils import flt, getdate, today, date_diff, add_days
from hrms.hr import utils as hrms_utils

@frappe.whitelist()
def get_dashboard_data(employee=None):
    """
    Get aggregated dashboard data for the employee:
    - Total Allocated Days (only vacation type, current year)
    - Total Consumed Days (only "Por Días" requests, not hours)
    - Balance (Remaining)
    - Available Leave Types
    """
    if not employee:
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
    if not employee:
        return {"error": "Employee not found"}

    today_date = getdate(today())
    current_year = today_date.year
    
    # Find the main vacation leave type
    vacation_leave_type = frappe.db.get_value("Spanish Leave Type", 
        {"leave_type_name": ["like", "%Vacaciones%"]}, "name")

    # Get allocations - filter by vacation type and current year
    alloc_filters = {
        "employee": employee,
        "docstatus": 1,
    }
    if vacation_leave_type:
        alloc_filters["leave_type"] = vacation_leave_type
    
    allocations = frappe.get_all(
        "Spanish Leave Allocation",
        filters=alloc_filters,
        fields=["days_allocated", "leave_type", "contract_start_date", "contract_end_date"]
    )

    # Aggregate Data (only days for vacations)
    dashboard = {
        "total_days_allocated": 0.0,
        "total_days_consumed": 0.0,
        "total_days_remaining": 0.0,
        "leave_types_config": {}
    }

    # Fetch Leave Type configs
    leave_types = frappe.get_all("Spanish Leave Type", fields=["name", "leave_type_name", "allow_hours_request", "hours_per_day", "allow_negative_balance"])
    lt_map = {lt.name: lt for lt in leave_types}

    # Only count allocations for current year - just get days_allocated
    for alloc in allocations:
        # Check if allocation is for current year
        alloc_start = getdate(alloc.contract_start_date) if alloc.contract_start_date else None
        alloc_end = getdate(alloc.contract_end_date) if alloc.contract_end_date else None
        
        # Include if: start year <= current year AND (no end date OR end year >= current year)
        is_current = False
        if alloc_start:
            if alloc_start.year <= current_year:
                if not alloc_end or alloc_end.year >= current_year:
                    is_current = True
        else:
            # No start date, include it
            is_current = True
        
        if is_current:
            dashboard["total_days_allocated"] += flt(alloc.days_allocated)

    # Calculate consumed days from approved applications (only "Por Días", not hours)
    # This ensures we don't count fractional days from hour-based requests
    consumed_filters = {
        "employee": employee,
        "status": "Aprobada",
        "request_type": "Por Días"
    }
    if vacation_leave_type:
        consumed_filters["leave_type"] = vacation_leave_type
    
    consumed_apps = frappe.get_all(
        "Spanish Leave Application",
        filters=consumed_filters,
        fields=["total_days", "from_date"]
    )
    
    # Only count consumed for current year
    for app in consumed_apps:
        app_date = getdate(app.from_date) if app.from_date else None
        if app_date and app_date.year == current_year:
            dashboard["total_days_consumed"] += flt(app.total_days)
    
    # Calculate remaining (allocated - consumed)
    dashboard["total_days_remaining"] = dashboard["total_days_allocated"] - dashboard["total_days_consumed"]

    # Calculate Pending Approval (User's own requests) - only vacation type and current year
    pending_filters = {
        "employee": employee, 
        "status": "Abierta",
        "request_type": "Por Días"
    }
    if vacation_leave_type:
        pending_filters["leave_type"] = vacation_leave_type
    
    pending_apps = frappe.get_all(
        "Spanish Leave Application",
        filters=pending_filters,
        fields=["total_days", "from_date", "request_date"]
    )
    
    # Only count pending for current year
    days_pending = 0.0
    for app in pending_apps:
        app_date = getdate(app.from_date or app.request_date) if (app.from_date or app.request_date) else None
        if app_date and app_date.year == current_year:
            days_pending += flt(app.total_days)
    
    dashboard["total_days_pending"] = days_pending

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
    # Convert string to boolean (Frappe sends "true"/"false" as strings)
    if isinstance(only_my_team, str):
        only_my_team = only_my_team.lower() == "true"
    
    filters = {}
    
    # Permission Filter
    # Prioridad: Validar HC > Validador HR > Responsable Departamento > otros
    roles = frappe.get_roles(frappe.session.user)
    if frappe.session.user != "Administrator":
        if "Validar HC" in roles or "Validador HR" in roles:
            # Usuarios con permisos amplios: pueden ver todo o solo su equipo según checkbox
            if only_my_team:
                filters["leave_approver"] = frappe.session.user
            # Si only_my_team es False, no se aplica filtro de leave_approver (ven todos)
        elif "Responsable Departamento" in roles:
            # Responsables de departamento siempre ven solo su equipo
            filters["leave_approver"] = frappe.session.user
        else:
            # Otros usuarios solo ven su equipo
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
def get_team_leaves(month_start=None, month_end=None, employee=None, leave_type=None, location=None, only_my_team=None):
    """
    Get approved and pending leaves for the team calendar/gantt
    Includes both 'Aprobada' and 'Abierta' (pending) requests for planning
    """
    # Convert string to boolean (Frappe sends "true"/"false" as strings)
    if isinstance(only_my_team, str):
        only_my_team = only_my_team.lower() == "true"
    
    filters = {
        "status": ["in", ["Aprobada", "Abierta"]], 
    }
    
    # Permission Filter
    # Prioridad: Validar HC > Validador HR > Responsable Departamento > otros
    roles = frappe.get_roles(frappe.session.user)
    if frappe.session.user != "Administrator":
        if "Validar HC" in roles or "Validador HR" in roles:
            # Usuarios con permisos amplios: pueden ver todo o solo su equipo según checkbox
            if only_my_team:
                filters["leave_approver"] = frappe.session.user
            # Si only_my_team es False, no se aplica filtro de leave_approver (ven todos)
        elif "Responsable Departamento" in roles:
            # Responsables de departamento siempre ven solo su equipo
            filters["leave_approver"] = frappe.session.user
        else:
            # Otros usuarios solo ven su equipo
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
    
    today_date = getdate(today())
    
    if doc.request_type == "Por Días":
        doc.from_date = getdate(data.get("from_date"))
        doc.to_date = getdate(data.get("to_date"))
        
        # Validar que las fechas no sean en el pasado
        if doc.from_date < today_date:
            frappe.throw(_("No puedes solicitar vacaciones con fecha de inicio en el pasado."))
        if doc.to_date < doc.from_date:
            frappe.throw(_("La fecha de fin no puede ser anterior a la fecha de inicio."))
    else:
        doc.request_date = getdate(data.get("request_date"))
        
        # Validar que la fecha no sea en el pasado
        if doc.request_date < today_date:
            frappe.throw(_("No puedes solicitar horas en una fecha pasada."))
        
        doc.total_hours = flt(data.get("hours", 0))
        if doc.total_hours <= 0:
            frappe.throw(_("La cantidad de horas debe ser mayor a 0."))
    
    doc.insert(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def process_request(name, action, reason=None):
    """
    Approve, Reject or Cancel a request
    action: 'approve' | 'reject' | 'cancel'
    reason: Optional rejection reason (only used when action='reject')
    """
    doc = frappe.get_doc("Spanish Leave Application", name)
    
    # Validate permissions - approver, HR roles or Administrator
    roles = frappe.get_roles(frappe.session.user)
    is_authorized = (
        doc.leave_approver == frappe.session.user or 
        "Validar HC" in roles or 
        "Validador HR" in roles or
        frappe.session.user == "Administrator"
    )
    
    if not is_authorized:
        frappe.throw(_("No tienes permiso para procesar esta solicitud."))
        
    if action == "approve":
        doc.status = "Aprobada"
        # Usar ignore_permissions porque el aprobador ya fue validado arriba
        # y necesita poder actualizar asignaciones automáticamente
        doc.flags.ignore_permissions = True
        doc.submit()
    elif action == "reject":
        doc.status = "Rechazada"
        doc.flags.ignore_permissions = True
        doc.save()
        # Añadir motivo de rechazo como comentario si se proporciona
        if reason:
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": "Spanish Leave Application",
                "reference_name": name,
                "content": f"Motivo del rechazo: {reason}"
            }).insert(ignore_permissions=True)
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
def get_team_vacation_summary(leave_type=None, location=None, only_my_team=None, employee=None):
    """
    Get vacation summary for each team member.
    Returns aggregated data per employee:
    - Total allocated days
    - Approved days (total)
    - Enjoyed days (already taken - past dates)
    - Pending approval days
    - Approved not enjoyed (future approved)
    - Remaining days
    """
    # Convert string to boolean (Frappe sends "true"/"false" as strings)
    if isinstance(only_my_team, str):
        only_my_team = only_my_team.lower() == "true"
    
    # Get team members based on permissions
    filters = {"status": "Active"}
    
    # Permission Filter
    # Prioridad: Validar HC > Validador HR > Responsable Departamento > otros
    roles = frappe.get_roles(frappe.session.user)
    if frappe.session.user != "Administrator":
        if "Validar HC" in roles or "Validador HR" in roles:
            # Usuarios con permisos amplios: pueden ver todo o solo su equipo según checkbox
            if only_my_team:
                filters["leave_approver"] = frappe.session.user
            # Si only_my_team es False, no se aplica filtro de leave_approver (ven todos)
        elif "Responsable Departamento" in roles:
            # Responsables de departamento siempre ven solo su equipo
            filters["leave_approver"] = frappe.session.user
        else:
            # Otros usuarios solo ven su equipo
            filters["leave_approver"] = frappe.session.user
    
    # Filter by specific employee if provided
    if employee:
        filters["name"] = employee
    
    # Filter by location/centro
    if location:
        filters["custom_centro"] = location
    
    employees = frappe.get_all("Employee", 
        filters=filters,
        fields=["name", "employee_name", "custom_centro", "image", "designation"],
        order_by="employee_name asc"
    )
    
    if not employees:
        return []
    
    employee_ids = [e.name for e in employees]
    today_date = getdate(today())
    
    # Default leave type for vacations - get the main vacation type
    vacation_leave_type = leave_type
    if not vacation_leave_type:
        # Try to find the standard vacation leave type
        vacation_leave_type = frappe.db.get_value("Spanish Leave Type", 
            {"leave_type_name": ["like", "%Vacaciones%"]}, "name")
    
    result = []
    current_year = today_date.year
    
    for emp in employees:
        emp_data = {
            "employee": emp.name,
            "employee_name": emp.employee_name,
            "designation": emp.designation,
            "centro": emp.custom_centro,
            "image": emp.image,
            "allocated": 0,
            "consumed": 0,  # Total consumido (de la asignación)
            "remaining": 0,  # Saldo disponible (de la asignación)
            "pending_approval": 0,  # Días en solicitudes pendientes
            "enjoyed": 0,  # Días ya disfrutados (fechas pasadas)
            "approved_not_enjoyed": 0  # Días aprobados pero futuros
        }
        
        # Get allocations for this employee - only current year or active contracts
        alloc_filters = {
            "employee": emp.name,
            "docstatus": 1
        }
        if vacation_leave_type:
            alloc_filters["leave_type"] = vacation_leave_type
            
        allocations = frappe.get_all(
            "Spanish Leave Allocation",
            filters=alloc_filters,
            fields=["days_allocated", "days_consumed", "days_remaining", "contract_start_date", "contract_end_date"],
            order_by="contract_start_date desc"
        )
        
        # Filter allocations: only those that overlap with current year
        for alloc in allocations:
            # Check if allocation is for current year
            alloc_start = getdate(alloc.contract_start_date) if alloc.contract_start_date else None
            alloc_end = getdate(alloc.contract_end_date) if alloc.contract_end_date else None
            
            # Include if: start year <= current year AND (no end date OR end year >= current year)
            is_current = False
            if alloc_start:
                if alloc_start.year <= current_year:
                    if not alloc_end or alloc_end.year >= current_year:
                        is_current = True
            else:
                # No start date, include it
                is_current = True
            
            if is_current:
                emp_data["allocated"] += flt(alloc.days_allocated)
                emp_data["consumed"] += flt(alloc.days_consumed)
                emp_data["remaining"] += flt(alloc.days_remaining)
        
        # Get applications for this employee - current year only
        app_filters = {
            "employee": emp.name,
            "request_type": "Por Días"
        }
        if vacation_leave_type:
            app_filters["leave_type"] = vacation_leave_type
        
        applications = frappe.get_all(
            "Spanish Leave Application",
            filters=app_filters,
            fields=["status", "from_date", "to_date", "total_days"]
        )
        
        for app in applications:
            # Only count applications that start in current year
            app_start = getdate(app.from_date) if app.from_date else None
            if app_start and app_start.year != current_year:
                continue
                
            if app.status == "Abierta":
                emp_data["pending_approval"] += flt(app.total_days)
            elif app.status == "Aprobada":
                # Check if already enjoyed (past) or future
                if app.to_date and getdate(app.to_date) < today_date:
                    emp_data["enjoyed"] += flt(app.total_days)
                else:
                    emp_data["approved_not_enjoyed"] += flt(app.total_days)
        
        result.append(emp_data)
    
    return result


@frappe.whitelist()
def get_employee_leave_detail(employee):
    """
    Get detailed leave information for a specific employee.
    Returns vacation allocations and applications (only "Vacaciones" type, only days).
    Shows all statuses: Abierta, Aprobada, Rechazada, Cancelada.
    """
    # Verify permission
    roles = frappe.get_roles(frappe.session.user)
    emp_approver = frappe.db.get_value("Employee", employee, "leave_approver")
    
    is_authorized = (
        emp_approver == frappe.session.user or
        "Validar HC" in roles or
        "Validador HR" in roles or
        frappe.session.user == "Administrator"
    )
    
    if not is_authorized:
        frappe.throw(_("No tienes permiso para ver esta información."))
    
    # Get employee info
    emp_info = frappe.db.get_value("Employee", employee, 
        ["name", "employee_name", "custom_centro", "image", "designation", "department"],
        as_dict=True
    )
    
    if not emp_info:
        frappe.throw(_("Empleado no encontrado."))
    
    # Get centro name
    centro_name = None
    if emp_info.custom_centro:
        centro_name = frappe.db.get_value("Room", emp_info.custom_centro, "room_name")
    
    # Find the main vacation leave type
    vacation_leave_type = frappe.db.get_value("Spanish Leave Type",
        {"leave_type_name": ["like", "%Vacaciones%"]}, "name")
    
    # Get leave type names map
    leave_types = {lt.name: lt.leave_type_name for lt in frappe.get_all(
        "Spanish Leave Type", fields=["name", "leave_type_name"]
    )}
    
    # Get allocations - only vacation type
    alloc_filters = {"employee": employee, "docstatus": 1}
    if vacation_leave_type:
        alloc_filters["leave_type"] = vacation_leave_type
    
    allocations = frappe.get_all(
        "Spanish Leave Allocation",
        filters=alloc_filters,
        fields=["name", "leave_type", "days_allocated", 
                "days_consumed", "days_remaining",
                "contract_start_date", "contract_end_date", "owner", "creation"],
        order_by="contract_start_date desc"
    )
    
    for alloc in allocations:
        alloc["leave_type_name"] = leave_types.get(alloc.leave_type, alloc.leave_type)
        # Get the full name of who created the allocation
        if alloc.owner:
            owner_name = frappe.db.get_value("User", alloc.owner, "full_name")
            alloc["created_by_name"] = owner_name or alloc.owner
        else:
            alloc["created_by_name"] = "-"
    
    # Get applications - only vacation type and "Por Días" (all statuses)
    app_filters = {
        "employee": employee,
        "request_type": "Por Días"  # Only days, no hours
    }
    if vacation_leave_type:
        app_filters["leave_type"] = vacation_leave_type
    
    applications = frappe.get_all(
        "Spanish Leave Application",
        filters=app_filters,
        fields=["name", "leave_type", "status", "from_date", "to_date", 
                "total_days", "request_type", "description",
                "request_date", "creation", "modified"],
        order_by="creation desc"
    )
    
    for app in applications:
        app["leave_type_name"] = leave_types.get(app.leave_type, app.leave_type)
    
    # Calculate summary stats (only days, only vacations)
    today_date = getdate(today())
    current_year = today_date.year
    
    # Filter allocations for current year
    total_allocated = 0
    total_consumed = 0
    total_remaining = 0
    for alloc in allocations:
        alloc_start = getdate(alloc.contract_start_date) if alloc.contract_start_date else None
        alloc_end = getdate(alloc.contract_end_date) if alloc.contract_end_date else None
        
        is_current = False
        if alloc_start:
            if alloc_start.year <= current_year:
                if not alloc_end or alloc_end.year >= current_year:
                    is_current = True
        else:
            is_current = True
        
        if is_current:
            total_allocated += flt(alloc.days_allocated)
            total_consumed += flt(alloc.days_consumed)
            total_remaining += flt(alloc.days_remaining)
    
    # Calculate pending and approved future from applications (current year only)
    pending_approval = 0
    approved_future = 0
    for app in applications:
        app_start = getdate(app.from_date) if app.from_date else None
        if app_start and app_start.year != current_year:
            continue
        
        if app.status == "Abierta":
            pending_approval += flt(app.total_days)
        elif app.status == "Aprobada":
            if app.to_date and getdate(app.to_date) >= today_date:
                approved_future += flt(app.total_days)
    
    summary = {
        "total_allocated": total_allocated,
        "total_remaining": total_remaining,
        "total_consumed": total_consumed,
        "pending_approval": pending_approval,
        "approved_future": approved_future,
    }
    
    return {
        "employee": emp_info,
        "centro_name": centro_name,
        "allocations": allocations,
        "applications": applications,
        "summary": summary
    }


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


@frappe.whitelist()
def create_leave_allocation(employee, days_allocated, contract_start_date=None, contract_end_date=None):
    """
    Create a new Spanish Leave Allocation for an employee.
    Only managers/approvers can create allocations for their team.
    """
    from frappe import _
    
    # Verify permission - user must be the employee's approver or have Validar HC/Validador HR role
    emp_approver = frappe.db.get_value("Employee", employee, "leave_approver")
    roles = frappe.get_roles(frappe.session.user)
    
    is_authorized = (
        emp_approver == frappe.session.user or
        "Validar HC" in roles or
        "Validador HR" in roles or
        frappe.session.user == "Administrator"
    )
    
    if not is_authorized:
        frappe.throw(_("No tienes permiso para crear asignaciones para este empleado."))
    
    # Validate days_allocated
    days = flt(days_allocated)
    if days <= 0:
        frappe.throw(_("Los días asignados deben ser mayor que 0."))
    
    # Find vacation leave type
    vacation_leave_type = frappe.db.get_value("Spanish Leave Type",
        {"leave_type_name": ["like", "%Vacaciones%"]}, "name")
    
    if not vacation_leave_type:
        frappe.throw(_("No se encontró el tipo de licencia 'Vacaciones'."))
    
    # Get employee name
    employee_name = frappe.db.get_value("Employee", employee, "employee_name")
    if not employee_name:
        frappe.throw(_("Empleado no encontrado."))
    
    # Get hours per day from leave type config (default 8)
    hours_per_day = flt(frappe.db.get_value("Spanish Leave Type", vacation_leave_type, "hours_per_day")) or 8.0
    
    # Ensure dates have default values (current year if not provided)
    current_year = getdate(today()).year
    if not contract_start_date or contract_start_date == '':
        contract_start_date = f"{current_year}-01-01"
    if not contract_end_date or contract_end_date == '':
        contract_end_date = f"{current_year}-12-31"
    
    # Calculate hours
    hours = days * hours_per_day
    
    # Create the allocation
    allocation = frappe.new_doc("Spanish Leave Allocation")
    allocation.employee = employee
    allocation.employee_name = employee_name
    allocation.leave_type = vacation_leave_type
    allocation.source_type = "Manual"
    # For Manual allocations, we need to set the _manual fields
    # because calculate_allocation() copies them to the main fields
    allocation.days_allocated_manual = days
    allocation.hours_allocated_manual = hours
    allocation.hours_per_day_manual = hours_per_day
    allocation.contract_start_date = contract_start_date
    allocation.contract_end_date = contract_end_date
    
    allocation.insert(ignore_permissions=True)
    allocation.submit()
    
    return {
        "success": True,
        "message": f"Asignación de {int(days)} días creada correctamente.",
        "name": allocation.name
    }
