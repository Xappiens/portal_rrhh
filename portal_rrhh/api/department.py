import frappe
from frappe import _
from frappe.utils import getdate, today, add_days, date_diff, nowdate, get_first_day, get_last_day, flt
from datetime import datetime, timedelta


def get_managed_employees(user=None):
    """
    Get employees that the current user manages (as department head).
    Returns a list of employee IDs that this user can manage.
    """
    if not user:
        user = frappe.session.user
    
    if user == "Administrator":
        # Admin sees all active employees
        return frappe.get_all("Employee", filters={"status": "Active"}, pluck="name")
    
    roles = frappe.get_roles(user)
    
    # Check if user has management roles
    is_hr_manager = "HR Manager" in roles or "HR User" in roles
    is_dept_manager = "Responsable de Departamento" in roles or "Responsable Departamento" in roles
    
    if is_hr_manager:
        # HR managers can see all employees
        return frappe.get_all("Employee", filters={"status": "Active"}, pluck="name")
    
    allowed_employees = set()
    
    # Get employees where this user is leave_approver
    employees_by_approver = frappe.get_all(
        "Employee",
        filters={"leave_approver": user, "status": "Active"},
        pluck="name"
    )
    allowed_employees.update(employees_by_approver)
    
    # Get employees where this user is reports_to (through Employee link)
    user_employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if user_employee:
        employees_by_reports_to = frappe.get_all(
            "Employee",
            filters={"reports_to": user_employee, "status": "Active"},
            pluck="name"
        )
        allowed_employees.update(employees_by_reports_to)
    
    # Get departments where this user is an approver
    if is_dept_manager:
        managed_departments = frappe.get_all(
            "Department Approver",
            filters={
                "approver": user,
                "parentfield": ["in", ["leave_approvers", "expense_approvers", "shift_request_approver"]]
            },
            pluck="parent"
        )
        
        if managed_departments:
            dept_employees = frappe.get_all(
                "Employee",
                filters={"status": "Active", "department": ["in", managed_departments]},
                pluck="name"
            )
            allowed_employees.update(dept_employees)
    
    return list(allowed_employees)


@frappe.whitelist()
def get_department_dashboard():
    """
    Get comprehensive dashboard data for department managers.
    Returns summary statistics and data for:
    - Team overview
    - Leave requests (pending/approved/rejected)
    - Attendance summary
    - Job offers
    - Timesheets
    """
    user = frappe.session.user
    managed_employees = get_managed_employees(user)
    
    if not managed_employees:
        return {
            "success": False,
            "message": _("No tienes empleados asignados para gestionar."),
            "data": None
        }
    
    today_date = getdate(today())
    current_month_start = get_first_day(today_date)
    current_month_end = get_last_day(today_date)
    week_start = today_date - timedelta(days=today_date.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get employee details
    employees = frappe.get_all(
        "Employee",
        filters={"name": ["in", managed_employees]},
        fields=[
            "name", "employee_name", "department", "designation", 
            "status", "date_of_joining", "image", "company_email",
            "personal_email", "cell_number", "custom_centro"
        ]
    )
    
    employee_map = {e.name: e for e in employees}
    
    # === TEAM SUMMARY ===
    team_summary = {
        "total_employees": len(employees),
        "active_employees": len([e for e in employees if e.status == "Active"]),
        "departments": list(set([e.department for e in employees if e.department])),
        "designations": list(set([e.designation for e in employees if e.designation]))
    }
    
    # === LEAVE REQUESTS (Spanish Leave Application) ===
    # Pending requests
    pending_leaves = frappe.get_all(
        "Spanish Leave Application",
        filters={
            "employee": ["in", managed_employees],
            "status": "Abierta"
        },
        fields=[
            "name", "employee", "employee_name", "leave_type", "status",
            "from_date", "to_date", "total_days", "request_type", "total_hours",
            "description", "request_date", "creation"
        ],
        order_by="creation desc"
    )
    
    # Approved leaves this month
    approved_leaves_month = frappe.get_all(
        "Spanish Leave Application",
        filters={
            "employee": ["in", managed_employees],
            "status": "Aprobada",
            "from_date": ["<=", current_month_end],
            "to_date": [">=", current_month_start]
        },
        fields=[
            "name", "employee", "employee_name", "leave_type", "status",
            "from_date", "to_date", "total_days", "request_type", "total_hours"
        ],
        order_by="from_date asc"
    )
    
    # Upcoming leaves (next 30 days)
    upcoming_leaves = frappe.get_all(
        "Spanish Leave Application",
        filters={
            "employee": ["in", managed_employees],
            "status": "Aprobada",
            "from_date": ["between", [today_date, add_days(today_date, 30)]]
        },
        fields=[
            "name", "employee", "employee_name", "leave_type",
            "from_date", "to_date", "total_days"
        ],
        order_by="from_date asc"
    )
    
    # Count by leave type
    leave_type_counts = {}
    for leave in approved_leaves_month:
        lt = leave.leave_type or "Sin tipo"
        leave_type_counts[lt] = leave_type_counts.get(lt, 0) + 1
    
    leave_summary = {
        "pending_count": len(pending_leaves),
        "pending_requests": pending_leaves,
        "approved_this_month": len(approved_leaves_month),
        "approved_leaves_month": approved_leaves_month,
        "upcoming_leaves": upcoming_leaves,
        "by_type": leave_type_counts
    }
    
    # === ATTENDANCE SUMMARY ===
    # Today's attendance
    today_attendances = frappe.get_all(
        "Attendance",
        filters={
            "employee": ["in", managed_employees],
            "attendance_date": today_date,
            "docstatus": ["!=", 2]
        },
        fields=["employee", "status", "in_time", "out_time", "working_hours"]
    )
    
    present_today = [a for a in today_attendances if a.status == "Present"]
    absent_today = [a for a in today_attendances if a.status == "Absent"]
    on_leave_today = [a for a in today_attendances if a.status == "On Leave"]
    wfh_today = [a for a in today_attendances if a.status == "Work From Home"]
    
    # Employees without attendance today
    employees_with_attendance = [a.employee for a in today_attendances]
    employees_without_attendance = [e for e in managed_employees if e not in employees_with_attendance]
    
    # This week checkins
    week_checkins = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": ["in", managed_employees],
            "time": ["between", [week_start, week_end + timedelta(days=1)]]
        },
        fields=["employee", "time", "log_type"]
    )
    
    # Group by employee and count checkins per day
    checkin_summary = {}
    for checkin in week_checkins:
        emp = checkin.employee
        if emp not in checkin_summary:
            checkin_summary[emp] = {"total_checkins": 0, "days_worked": set()}
        checkin_summary[emp]["total_checkins"] += 1
        checkin_summary[emp]["days_worked"].add(checkin.time.date())
    
    # Convert sets to counts
    for emp in checkin_summary:
        checkin_summary[emp]["days_worked"] = len(checkin_summary[emp]["days_worked"])
    
    attendance_summary = {
        "today": {
            "total": len(today_attendances),
            "present": len(present_today),
            "absent": len(absent_today),
            "on_leave": len(on_leave_today),
            "wfh": len(wfh_today),
            "no_record": len(employees_without_attendance)
        },
        "employees_without_attendance_today": [
            {
                "name": e,
                "employee_name": employee_map.get(e, {}).get("employee_name", e)
            }
            for e in employees_without_attendance[:10]  # Limit to 10
        ],
        "week_checkins": checkin_summary
    }
    
    # === JOB OFFERS ===
    # Get DNIs of managed employees
    employee_dnis = []
    for emp in employees:
        dni = frappe.db.get_value("Employee", emp.name, "custom_dninie")
        if dni:
            employee_dnis.append(dni)
    
    job_offers = []
    if employee_dnis:
        job_offers = frappe.get_all(
            "Job Offer",
            filters={"custom_dninie": ["in", employee_dnis]},
            fields=[
                "name", "applicant_name", "status", "workflow_state",
                "designation", "company", "custom_fecha_inicio", "custom_fecha_fin",
                "custom_tipo_de_contrato", "custom_estado_de_tramitacion",
                "custom_empleado"
            ],
            order_by="custom_fecha_inicio desc"
        )
    
    # Active job offers (Alta)
    active_job_offers = [jo for jo in job_offers if jo.workflow_state == "Alta"]
    
    # Expiring soon (within 30 days)
    expiring_soon = []
    for jo in active_job_offers:
        if jo.custom_fecha_fin:
            end_date = getdate(jo.custom_fecha_fin)
            days_until_expiry = date_diff(end_date, today_date)
            if 0 <= days_until_expiry <= 30:
                jo["days_until_expiry"] = days_until_expiry
                expiring_soon.append(jo)
    
    job_offer_summary = {
        "total": len(job_offers),
        "active": len(active_job_offers),
        "expiring_soon": expiring_soon,
        "recent": job_offers[:5]  # Last 5
    }
    
    # === TIMESHEETS ===
    # This month timesheets
    timesheets = frappe.get_all(
        "Timesheet",
        filters={
            "employee": ["in", managed_employees],
            "start_date": [">=", current_month_start],
            "docstatus": ["!=", 2]
        },
        fields=[
            "name", "employee", "employee_name", "status", "total_hours",
            "start_date", "end_date", "docstatus"
        ],
        order_by="start_date desc"
    )
    
    # Group by status
    ts_draft = [t for t in timesheets if t.docstatus == 0]
    ts_submitted = [t for t in timesheets if t.docstatus == 1]
    
    # Total hours this month
    total_hours = sum([flt(t.total_hours) for t in timesheets])
    
    timesheet_summary = {
        "total": len(timesheets),
        "draft": len(ts_draft),
        "submitted": len(ts_submitted),
        "total_hours": round(total_hours, 2),
        "recent": timesheets[:5]
    }
    
    # === CALENDAR EVENTS (Leaves for calendar view) ===
    calendar_events = []
    
    # Add approved leaves
    for leave in approved_leaves_month:
        calendar_events.append({
            "id": leave.name,
            "title": f"{leave.employee_name} - {leave.leave_type}",
            "start": str(leave.from_date),
            "end": str(leave.to_date),
            "type": "leave",
            "color": "#EF4444"  # Red for leaves
        })
    
    # Add upcoming leaves
    for leave in upcoming_leaves:
        if leave.name not in [e["id"] for e in calendar_events]:
            calendar_events.append({
                "id": leave.name,
                "title": f"{leave.employee_name} - {leave.leave_type}",
                "start": str(leave.from_date),
                "end": str(leave.to_date),
                "type": "leave",
                "color": "#F59E0B"  # Orange for upcoming
            })
    
    return {
        "success": True,
        "data": {
            "team_summary": team_summary,
            "leave_summary": leave_summary,
            "attendance_summary": attendance_summary,
            "job_offer_summary": job_offer_summary,
            "timesheet_summary": timesheet_summary,
            "calendar_events": calendar_events,
            "employees": employees
        }
    }


@frappe.whitelist()
def get_team_members():
    """
    Get list of team members for the current manager.
    """
    user = frappe.session.user
    managed_employees = get_managed_employees(user)
    
    if not managed_employees:
        return []
    
    employees = frappe.get_all(
        "Employee",
        filters={"name": ["in", managed_employees]},
        fields=[
            "name", "employee_name", "department", "designation",
            "status", "date_of_joining", "image", "company_email",
            "personal_email", "cell_number", "custom_centro",
            "leave_approver", "reports_to"
        ],
        order_by="employee_name asc"
    )
    
    # Enrich with additional data
    for emp in employees:
        # Get pending leave count
        emp["pending_leaves"] = frappe.db.count(
            "Spanish Leave Application",
            filters={"employee": emp.name, "status": "Abierta"}
        )
        
        # Get today's attendance
        today_attendance = frappe.db.get_value(
            "Attendance",
            {"employee": emp.name, "attendance_date": today(), "docstatus": ["!=", 2]},
            ["status", "in_time", "out_time"],
            as_dict=True
        )
        emp["today_attendance"] = today_attendance
        
        # Get active job offer count
        dni = frappe.db.get_value("Employee", emp.name, "custom_dninie")
        if dni:
            emp["active_job_offers"] = frappe.db.count(
                "Job Offer",
                filters={"custom_dninie": dni, "workflow_state": "Alta"}
            )
        else:
            emp["active_job_offers"] = 0
    
    return employees


@frappe.whitelist()
def get_pending_approvals():
    """
    Get all pending approvals for the current manager.
    Includes: Leave requests, Attendance regularization, etc.
    """
    user = frappe.session.user
    
    # Pending leave requests where user is approver
    pending_leaves = frappe.get_all(
        "Spanish Leave Application",
        filters={
            "leave_approver": user,
            "status": "Abierta"
        },
        fields=[
            "name", "employee", "employee_name", "leave_type", "status",
            "from_date", "to_date", "total_days", "request_type", "total_hours",
            "description", "request_date", "creation"
        ],
        order_by="creation desc"
    )
    
    # Add attachments
    if pending_leaves:
        leave_names = [l.name for l in pending_leaves]
        files = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Spanish Leave Application",
                "attached_to_name": ["in", leave_names]
            },
            fields=["file_url", "attached_to_name"]
        )
        file_map = {f.attached_to_name: f.file_url for f in files}
        for l in pending_leaves:
            l["attachment"] = file_map.get(l.name)
    
    # Get pending attendance requests if doctype exists
    pending_attendance_requests = []
    if frappe.db.table_exists("tabAttendance Request"):
        pending_attendance_requests = frappe.get_all(
            "Attendance Request",
            filters={
                "employee": ["in", get_managed_employees(user)],
                "docstatus": 0
            },
            fields=["name", "employee", "employee_name", "from_date", "to_date", "reason"]
        )
    
    return {
        "leave_requests": pending_leaves,
        "attendance_requests": pending_attendance_requests,
        "total_pending": len(pending_leaves) + len(pending_attendance_requests)
    }


@frappe.whitelist()
def approve_leave_request(name, action):
    """
    Approve or reject a leave request.
    action: 'approve' | 'reject'
    """
    doc = frappe.get_doc("Spanish Leave Application", name)
    
    # Validate permissions
    if doc.leave_approver != frappe.session.user and frappe.session.user != "Administrator":
        frappe.throw(_("No tienes permiso para procesar esta solicitud."))
    
    if action == "approve":
        doc.status = "Aprobada"
        doc.flags.ignore_permissions = True
        doc.submit()
    elif action == "reject":
        doc.status = "Rechazada"
        doc.save()
    else:
        frappe.throw(_("Acción no válida"))
    
    return {
        "success": True,
        "status": doc.status,
        "message": _("Solicitud {0}").format("aprobada" if action == "approve" else "rechazada")
    }


@frappe.whitelist()
def get_attendance_overview(from_date=None, to_date=None):
    """
    Get attendance overview for managed employees.
    """
    user = frappe.session.user
    managed_employees = get_managed_employees(user)
    
    if not managed_employees:
        return {"success": False, "data": []}
    
    if not from_date:
        from_date = get_first_day(today())
    if not to_date:
        to_date = get_last_day(today())
    
    from_date = getdate(from_date)
    to_date = getdate(to_date)
    
    # Get all attendance records
    attendances = frappe.get_all(
        "Attendance",
        filters={
            "employee": ["in", managed_employees],
            "attendance_date": ["between", [from_date, to_date]],
            "docstatus": ["!=", 2]
        },
        fields=["employee", "attendance_date", "status", "working_hours", "in_time", "out_time"]
    )
    
    # Get employee names
    employees = frappe.get_all(
        "Employee",
        filters={"name": ["in", managed_employees]},
        fields=["name", "employee_name"]
    )
    emp_map = {e.name: e.employee_name for e in employees}
    
    # Organize by employee
    attendance_by_employee = {}
    for emp in managed_employees:
        attendance_by_employee[emp] = {
            "employee_name": emp_map.get(emp, emp),
            "days": {},
            "summary": {
                "present": 0,
                "absent": 0,
                "on_leave": 0,
                "wfh": 0,
                "total_hours": 0
            }
        }
    
    for att in attendances:
        emp = att.employee
        date_str = str(att.attendance_date)
        
        attendance_by_employee[emp]["days"][date_str] = {
            "status": att.status,
            "working_hours": att.working_hours,
            "in_time": str(att.in_time) if att.in_time else None,
            "out_time": str(att.out_time) if att.out_time else None
        }
        
        # Update summary
        if att.status == "Present":
            attendance_by_employee[emp]["summary"]["present"] += 1
        elif att.status == "Absent":
            attendance_by_employee[emp]["summary"]["absent"] += 1
        elif att.status == "On Leave":
            attendance_by_employee[emp]["summary"]["on_leave"] += 1
        elif att.status == "Work From Home":
            attendance_by_employee[emp]["summary"]["wfh"] += 1
        
        if att.working_hours:
            attendance_by_employee[emp]["summary"]["total_hours"] += flt(att.working_hours)
    
    # Round total hours
    for emp in attendance_by_employee:
        attendance_by_employee[emp]["summary"]["total_hours"] = round(
            attendance_by_employee[emp]["summary"]["total_hours"], 2
        )
    
    return {
        "success": True,
        "data": attendance_by_employee,
        "from_date": str(from_date),
        "to_date": str(to_date)
    }


@frappe.whitelist()
def get_leave_calendar(month=None, year=None):
    """
    Get leave calendar for managed employees.
    """
    user = frappe.session.user
    managed_employees = get_managed_employees(user)
    
    if not managed_employees:
        return []
    
    today_date = getdate(today())
    
    if not month:
        month = today_date.month
    if not year:
        year = today_date.year
    
    month = int(month)
    year = int(year)
    
    month_start = getdate(f"{year}-{month:02d}-01")
    month_end = get_last_day(month_start)
    
    # Get approved leaves
    leaves = frappe.get_all(
        "Spanish Leave Application",
        filters={
            "employee": ["in", managed_employees],
            "status": "Aprobada",
            "from_date": ["<=", month_end],
            "to_date": [">=", month_start]
        },
        fields=[
            "name", "employee", "employee_name", "leave_type",
            "from_date", "to_date", "total_days"
        ]
    )
    
    # Define colors for leave types
    leave_colors = {
        "Vacaciones": "#3B82F6",
        "Permiso Retribuido": "#10B981",
        "Permiso No Retribuido": "#F59E0B",
        "Baja Médica": "#EF4444",
        "default": "#6B7280"
    }
    
    events = []
    for leave in leaves:
        color = leave_colors.get(leave.leave_type, leave_colors["default"])
        events.append({
            "id": leave.name,
            "title": f"{leave.employee_name}",
            "subtitle": leave.leave_type,
            "start": str(leave.from_date),
            "end": str(leave.to_date),
            "color": color,
            "employee": leave.employee,
            "leave_type": leave.leave_type,
            "total_days": leave.total_days
        })
    
    return events


@frappe.whitelist()
def get_department_stats():
    """
    Get quick statistics for the department dashboard header.
    """
    user = frappe.session.user
    managed_employees = get_managed_employees(user)
    
    if not managed_employees:
        return {
            "team_size": 0,
            "pending_approvals": 0,
            "on_leave_today": 0,
            "present_today": 0
        }
    
    today_date = today()
    
    # Team size
    team_size = len(managed_employees)
    
    # Pending approvals
    pending_approvals = frappe.db.count(
        "Spanish Leave Application",
        filters={
            "leave_approver": user,
            "status": "Abierta"
        }
    )
    
    # On leave today
    on_leave_today = frappe.db.count(
        "Spanish Leave Application",
        filters={
            "employee": ["in", managed_employees],
            "status": "Aprobada",
            "from_date": ["<=", today_date],
            "to_date": [">=", today_date]
        }
    )
    
    # Present today
    present_today = frappe.db.count(
        "Attendance",
        filters={
            "employee": ["in", managed_employees],
            "attendance_date": today_date,
            "status": ["in", ["Present", "Work From Home"]],
            "docstatus": ["!=", 2]
        }
    )
    
    return {
        "team_size": team_size,
        "pending_approvals": pending_approvals,
        "on_leave_today": on_leave_today,
        "present_today": present_today
    }
