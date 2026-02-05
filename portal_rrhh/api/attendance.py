import frappe
from frappe import _
from frappe.utils import now, getdate, get_time, add_days, date_diff, today
from frappe.model.document import Document


@frappe.whitelist(allow_guest=False)
def get_attendance_report(employee, from_date, to_date):
    """
    Get attendance report for an employee for a date range.
    Returns daily hours worked, leave/holiday status, and anomalies.
    
    Anomalies detected:
    - missing_out: Tiene entrada pero no salida
    - missing_in: Tiene salida pero no entrada
    - no_break: Jornada > 6h sin descanso de al menos 15 minutos
    - no_checkin: Día laborable sin fichajes ni justificación
    """
    from datetime import timedelta
    
    if not employee:
        return {"success": False, "message": _("Employee is required")}
    
    if not from_date or not to_date:
        return {"success": False, "message": _("Dates are required")}
    
    start_date = getdate(from_date)
    end_date = getdate(to_date)
    today_date = getdate(today())
    
    # Verify the current user can access this employee's data
    current_user = frappe.session.user
    if current_user != "Administrator":
        user_employee = frappe.db.get_value("Employee", {"user_id": current_user}, "name")
        if user_employee != employee:
            roles = frappe.get_roles(current_user)
            if "HR Manager" not in roles and "HR User" not in roles:
                emp_approver = frappe.db.get_value("Employee", employee, "leave_approver")
                if emp_approver != current_user:
                    emp_dept = frappe.db.get_value("Employee", employee, "department")
                    is_dept_approver = frappe.db.exists("Department Approver", {
                        "parent": emp_dept,
                        "approver": current_user
                    })
                    if not is_dept_approver:
                        return {"success": False, "message": _("Not authorized to view this employee's data")}
    
    # Fetch checkins for anomaly detection
    checkins = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", [start_date, end_date + timedelta(days=1)]],
            "skip_auto_attendance": 0
        },
        fields=["time", "log_type"],
        order_by="time asc"
    )
    
    # Group checkins by date
    checkins_by_date = {}
    for c in checkins:
        d = c.time.date().strftime("%Y-%m-%d")
        if d not in checkins_by_date:
            checkins_by_date[d] = []
        checkins_by_date[d].append(c)
    
    # Fetch attendance records
    attendances = frappe.get_all(
        "Attendance",
        filters={
            "employee": employee,
            "attendance_date": ["between", [start_date, end_date]],
            "docstatus": ["!=", 2]
        },
        fields=["attendance_date", "status", "working_hours", "in_time", "out_time"]
    )
    attendance_map = {a.attendance_date.strftime("%Y-%m-%d"): a for a in attendances}
    
    # Fetch approved leaves (standard + Spanish)
    leaves = frappe.get_all(
        "Leave Application",
        filters={
            "employee": employee,
            "status": "Approved",
            "from_date": ["<=", end_date],
            "to_date": [">=", start_date]
        },
        fields=["from_date", "to_date", "leave_type"]
    )
    
    spanish_leaves = []
    if frappe.db.table_exists("tabSpanish Leave Application"):
        spanish_leaves = frappe.get_all(
            "Spanish Leave Application",
            filters={
                "employee": employee,
                "status": ["in", ["Aprobada", "Approved"]],
                "from_date": ["<=", end_date],
                "to_date": [">=", start_date]
            },
            fields=["from_date", "to_date", "leave_type"]
        )
    
    # Build leave map
    leave_map = {}
    for leave in leaves + spanish_leaves:
        l_start = max(leave.from_date, start_date)
        l_end = min(leave.to_date, end_date)
        days = date_diff(l_end, l_start)
        for i in range(days + 1):
            d = add_days(l_start, i).strftime("%Y-%m-%d")
            if d not in leave_map:
                leave_map[d] = []
            leave_map[d].append(leave.leave_type)
    
    # Get holidays
    holiday_list = frappe.db.get_value("Employee", employee, "holiday_list")
    holidays = set()
    if holiday_list:
        holiday_records = frappe.get_all(
            "Holiday",
            filters={
                "parent": holiday_list,
                "holiday_date": ["between", [start_date, end_date]]
            },
            pluck="holiday_date"
        )
        holidays = {h.strftime("%Y-%m-%d") for h in holiday_records}
    
    # Build result data
    result = []
    current = start_date
    
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        date_obj = current
        is_today = date_obj == today_date
        is_weekend = date_obj.weekday() >= 5  # Saturday=5, Sunday=6
        is_holiday = date_str in holidays
        has_leave = date_str in leave_map
        
        hours = 0
        status_list = []
        anomaly = None
        anomaly_desc = None
        
        # Get checkins for this day
        day_checkins = checkins_by_date.get(date_str, [])
        
        # Calculate hours from checkins (always, for any day with checkins)
        if day_checkins:
            sorted_checkins = sorted(day_checkins, key=lambda x: x.time)
            sessions = []
            current_in_time = None
            
            for c in sorted_checkins:
                if c.log_type == 'IN' and current_in_time is None:
                    current_in_time = c.time
                elif c.log_type == 'OUT' and current_in_time:
                    sessions.append((current_in_time, c.time))
                    current_in_time = None
            
            # Sum all completed sessions
            if sessions:
                total_seconds = sum((s[1] - s[0]).total_seconds() for s in sessions)
                hours = round(total_seconds / 3600.0, 1)
            
            # Analyze anomalies (only for past days, not today)
            if not is_today:
                ins = [c for c in day_checkins if c.log_type == 'IN']
                outs = [c for c in day_checkins if c.log_type == 'OUT']
                
                # Check missing punches
                if len(ins) > len(outs):
                    anomaly = "missing_out"
                    anomaly_desc = f"Falta salida ({len(ins)} entrada(s), {len(outs)} salida(s))"
                elif len(outs) > len(ins):
                    anomaly = "missing_in"
                    anomaly_desc = f"Falta entrada ({len(outs)} salida(s), {len(ins)} entrada(s))"
                else:
                    # Check for >6h continuous work without break
                    for s_in, s_out in sessions:
                        session_hours = (s_out - s_in).total_seconds() / 3600.0
                        if session_hours > 6:
                            anomaly = "no_break"
                            anomaly_desc = f"Sesión de {session_hours:.1f}h sin descanso"
                            break
                    
                    # Also flag if total >6h with only 1 session
                    if not anomaly and len(sessions) == 1 and hours > 6:
                        anomaly = "no_break"
                        anomaly_desc = f"Jornada de {hours}h sin descanso registrado"
        else:
            # No checkins - check attendance record as fallback
            if date_str in attendance_map:
                att = attendance_map[date_str]
                hours = round(att.working_hours or 0, 1)
                if att.status and att.status not in ["Present", "Work From Home"]:
                    status_list.append(att.status)
            
            # No checkins on a workday without justification (only for past days)
            if not is_today and not is_weekend and not is_holiday and not has_leave:
                if date_obj < today_date:
                    anomaly = "no_checkin"
                    anomaly_desc = "Sin fichaje ni justificación"
        
        # Check leaves
        if has_leave:
            status_list.extend(leave_map[date_str])
        
        # Check holidays
        if is_holiday:
            status_list.append("Festivo")
        
        result.append({
            "date": date_str,
            "hours": hours,
            "status": ", ".join(status_list) if status_list else None,
            "anomaly": anomaly,
            "anomaly_desc": anomaly_desc
        })
        
        current = add_days(current, 1)
    
    return {"success": True, "data": result}


@frappe.whitelist(allow_guest=False)
def mark_attendance(employee, status, attendance_date=None, in_time=None, out_time=None, shift=None):
    """
    Mark attendance for an employee
    """
    try:
        # Validate employee
        if not frappe.db.exists("Employee", employee):
            return {
                "success": False,
                "message": _("Employee not found")
            }

        # Set default values
        if not attendance_date:
            attendance_date = getdate()
        else:
            attendance_date = getdate(attendance_date)

        # Check if attendance already exists for this date
        existing_attendance = frappe.db.exists("Attendance", {
            "employee": employee,
            "attendance_date": attendance_date
        })

        if existing_attendance:
            return {
                "success": False,
                "message": _("Attendance already marked for this date")
            }

        # Create attendance record
        attendance = frappe.new_doc("Attendance")
        attendance.employee = employee
        attendance.employee_name = frappe.db.get_value("Employee", employee, "employee_name")
        attendance.attendance_date = attendance_date
        attendance.status = status
        attendance.company = frappe.db.get_value("Employee", employee, "company")
        attendance.department = frappe.db.get_value("Employee", employee, "department")

        if shift:
            attendance.shift = shift

        if in_time:
            attendance.in_time = in_time

        if out_time:
            attendance.out_time = out_time

        # Calculate working hours if both in_time and out_time are provided
        if in_time and out_time:
            in_time_obj = get_time(in_time)
            out_time_obj = get_time(out_time)
            if out_time_obj > in_time_obj:
                attendance.working_hours = (out_time_obj - in_time_obj).total_seconds() / 3600

        # Remove ignore_permissions to enforce strict RBAC
        attendance.insert()
        attendance.submit()

        return {
            "success": True,
            "message": _("Attendance marked successfully"),
            "attendance_id": attendance.name
        }

    except Exception as e:
        frappe.log_error(f"Error marking attendance: {str(e)}")
        return {
            "success": False,
            "message": _("Error marking attendance: {0}").format(str(e))
        }

@frappe.whitelist(allow_guest=False)
def save_verified_attendance(employee, date, total_hours, in_time=None, out_time=None, rest_time=None):
    """
    Creates or updates a Verified Attendance record.
    """
    # Strict Permission Check
    if not frappe.has_permission("Verified Attendance", "write"):
        # Double check 'System Manager' or 'HR Manager' as fallback if DocType permissions are weird
        roles = frappe.get_roles()
        if "System Manager" not in roles and "HR Manager" not in roles:
             return {"success": False, "message": _("No permission to verify attendance")}

    current_user = frappe.session.user
    from frappe.utils import getdate
    
    # Ensure date is a proper Date object for querying
    date_obj = getdate(date)
    emp_clean = employee.strip()
    
    # Deterministic Name for Consistency
    doc_name = f"{emp_clean}-{date_obj}"
    
    frappe.errprint(f"DEBUG: Verifying Attendance. ID: {doc_name} User: {current_user}")
    
    try:
        # We process as Current User to enforce permissions.
        # Removed frappe.set_user("Administrator")
        
        doc = None
        is_new = False

        # 1. Try Load
        if frappe.db.exists("Verified Attendance", doc_name):
            doc = frappe.get_doc("Verified Attendance", doc_name)
        else:
            # 2. Prepare New
            doc = frappe.new_doc("Verified Attendance")
            doc.name = doc_name # Enforce ID Strategy
            doc.employee = emp_clean
            doc.attendance_date = date_obj
            # Owner will be set automatically by insert if new
            is_new = True

        # 3. Set Values
        doc.total_hours = total_hours
        if in_time: doc.verified_in_time = in_time
        if out_time: doc.verified_out_time = out_time
        if rest_time: doc.rest_time = rest_time
        
        # 4. Save
        try:
            if is_new:
                doc.company = frappe.db.get_value("Employee", emp_clean, "company") # ensure company is set
                doc.insert()
            else:
                doc.save()
                
        except frappe.DuplicateEntryError:
            # Race condition or 'exists' lied. Reload and Update.
            frappe.errprint("DEBUG: Race condition caught. Updating existing.")
            doc = frappe.get_doc("Verified Attendance", doc_name)
            doc.total_hours = total_hours
            if in_time: doc.verified_in_time = in_time
            if out_time: doc.verified_out_time = out_time
            if rest_time: doc.rest_time = rest_time
            doc.save()
            
        frappe.errprint(f"DEBUG: Saved successfully: {doc.name}")
        
        return {"success": True, "message": _("Attendance Verified")}

    except Exception as e:
        frappe.log_error(title="Attendance Verify Error", message=str(e))
        return {"success": False, "message": str(e)}

@frappe.whitelist(allow_guest=False)
def get_attendance_anomalies(from_date, to_date, employee=None, reports_to=None, show_all=False):
    """
    Detect anomalies in attendance:
    - Ghost Employee: Job Offer en estado 'Alta' pero sin fichajes
    - Missing Punches: IN sin OUT o viceversa (excluyendo día actual)
    - Absent: Ausencias sin justificación
    - Time Issues: Jornadas > 6h sin descanso
    
    Por defecto filtra por el equipo del usuario actual para eficiencia.
    show_all=True solo funciona para usuarios HR.
    """
    from frappe.utils import getdate, add_days, date_diff, today as get_today, cint
    from datetime import timedelta
    
    if not from_date or not to_date:
        return {"success": False, "message": _("Dates are required")}
        
    start_date = getdate(from_date)
    end_date = getdate(to_date)
    today_date = getdate(get_today())
    
    current_user = frappe.session.user
    roles = frappe.get_roles(current_user)
    
    # Determine user permissions
    is_hr_user = (
        current_user == "Administrator" 
        or "HR Manager" in roles
        or "HR User" in roles
        or "Validar HC" in roles
    )
    
    # Get current employee
    current_emp = frappe.db.get_value("Employee", {"user_id": current_user}, "name")
    
    # Build list of allowed employee IDs based on user's team
    allowed_emp_ids = set()
    available_managers = []  # For frontend filter options
    
    if current_emp:
        # Direct reports (reports_to = current employee)
        direct_reports = frappe.get_all(
            "Employee",
            filters={"reports_to": current_emp, "status": "Active"},
            pluck="name"
        )
        allowed_emp_ids.update(direct_reports)
        if direct_reports:
            available_managers.append(current_emp)
    
    # Employees where user is leave_approver
    leave_approver_emps = frappe.get_all(
        "Employee",
        filters={"leave_approver": current_user, "status": "Active"},
        pluck="name"
    )
    allowed_emp_ids.update(leave_approver_emps)
    
    # Department approvers
    if "Responsable de Departamento" in roles or "Responsable Departamento" in roles:
        managed_depts = frappe.get_all(
            "Department Approver",
            filters={"approver": current_user},
            pluck="parent"
        )
        if managed_depts:
            dept_emps = frappe.get_all(
                "Employee",
                filters={"status": "Active", "department": ["in", managed_depts]},
                pluck="name"
            )
            allowed_emp_ids.update(dept_emps)
    
    # For HR users: if show_all, don't restrict. Otherwise use their team too.
    if is_hr_user and cint(show_all):
        # No restriction - will query all active employees
        emp_filters = {"status": "Active"}
    else:
        # Restrict to user's team
        if not allowed_emp_ids:
            return {"success": True, "data": [], "managers": []}
        emp_filters = {"status": "Active", "name": ["in", list(allowed_emp_ids)]}
    
    # Additional filters
    if employee:
        # Verify access if not HR
        if not is_hr_user and employee not in allowed_emp_ids:
            return {"success": True, "data": [], "managers": []}
        emp_filters["name"] = employee
    
    if reports_to:
        emp_filters["reports_to"] = reports_to
    
    # Fetch employees
    employees = frappe.get_all("Employee", 
        filters=emp_filters, 
        fields=["name", "employee_name", "department", "holiday_list", "job_applicant", "reports_to"]
    )
    
    if not employees:
        return {"success": True, "data": [], "managers": []}
    
    # Build available managers list from the employees we have access to
    manager_ids = set(e.reports_to for e in employees if e.reports_to)
    managers = []
    if manager_ids:
        managers = frappe.get_all("Employee", 
            filters={"name": ["in", list(manager_ids)]},
            fields=["name", "employee_name"]
        )
    
    emp_map = {e.name: e for e in employees}
    emp_ids = list(emp_map.keys())

    # 2. Ghost Employee Check - Job Offers in "Alta" workflow state
    # Efficient: Only check employees in our filtered list that have job_applicant
    job_applicants = [e.job_applicant for e in employees if e.job_applicant]
    ghost_candidates = set()
    
    if job_applicants:
        # Get Job Offers with workflow_state = 'Alta' (active employees who should be working)
        active_offers = frappe.get_all("Job Offer", 
            filters={
                "job_applicant": ["in", job_applicants], 
                "workflow_state": "Alta"
            },
            pluck="job_applicant"
        )
        active_offer_applicants = set(active_offers)
        
        # Get employees from our list who have active offers
        emps_with_active_offer = [
            e.name for e in employees 
            if e.job_applicant and e.job_applicant in active_offer_applicants
        ]
        
        if emps_with_active_offer:
            # Check which of these have ANY checkins (efficient query on filtered set)
            emps_with_checkins = set(frappe.get_all(
                "Employee Checkin",
                filters={"employee": ["in", emps_with_active_offer]},
                distinct=True,
                pluck="employee"
            ))
            
            # Ghost = active offer but no checkins
            ghost_candidates = set(emps_with_active_offer) - emps_with_checkins

    # 3. Fetch Data in Bulk for Date Range
    checkins = frappe.get_all("Employee Checkin",
        filters={
            "employee": ["in", emp_ids],
            "time": ["between", [start_date, end_date + timedelta(days=1)]],
            "skip_auto_attendance": 0
        },
        fields=["employee", "time", "log_type"],
        order_by="time asc"
    )
    
    attendances = frappe.get_all("Attendance",
        filters={
            "employee": ["in", emp_ids],
            "attendance_date": ["between", [start_date, end_date]]
        },
        fields=["employee", "attendance_date", "status", "late_entry", "early_exit", "in_time", "out_time"]
    )
    
    leaves = frappe.get_all("Leave Application",
        filters={
            "employee": ["in", emp_ids],
            "status": "Approved",
            "from_date": ["<=", end_date],
            "to_date": [">=", start_date]
        },
        fields=["employee", "from_date", "to_date", "leave_type"]
    )
    
    # Holidays by list
    holiday_lists = set(e.holiday_list for e in employees if e.holiday_list)
    holidays_map = {}
    
    if holiday_lists:
        for h in frappe.get_all("Holiday",
            filters={"parent": ["in", list(holiday_lists)], "holiday_date": ["between", [start_date, end_date]]},
            fields=["parent", "holiday_date"]
        ):
            holidays_map.setdefault(h.parent, set()).add(h.holiday_date)

    # 4. Organize Data by Employee -> Date
    data_map = {e: {} for e in emp_ids}
    
    for c in checkins:
        d = c.time.date().strftime("%Y-%m-%d")
        data_map[c.employee].setdefault(d, {"checkins": [], "attendance": None, "leave": None})
        data_map[c.employee][d]["checkins"].append(c)
        
    for a in attendances:
        d = a.attendance_date.strftime("%Y-%m-%d")
        data_map[a.employee].setdefault(d, {"checkins": [], "attendance": None, "leave": None})
        data_map[a.employee][d]["attendance"] = a
        
    for l in leaves:
        l_start = max(l.from_date, start_date)
        l_end = min(l.to_date, end_date)
        for i in range(date_diff(l_end, l_start) + 1):
            d = add_days(l_start, i).strftime("%Y-%m-%d")
            data_map[l.employee].setdefault(d, {"checkins": [], "attendance": None, "leave": None})
            data_map[l.employee][d]["leave"] = l

    # 5. Process Anomalies
    anomalies = []
    flagged_time_issues = set()  # Track (employee, date) to avoid duplicates
    
    for emp_id, days_data in data_map.items():
        emp = emp_map[emp_id]
        emp_holidays = holidays_map.get(emp.holiday_list, set())
        
        for date_str, info in days_data.items():
            date_obj = getdate(date_str)
            logs = info.get("checkins", [])
            att = info.get("attendance")
            leave = info.get("leave")
            is_holiday = date_obj in emp_holidays
            is_today = date_obj == today_date
            
            if logs:
                ins = [l for l in logs if l.log_type == 'IN']
                outs = [l for l in logs if l.log_type == 'OUT']
                
                # Missing Punch - SKIP for current day (employee may not have clocked out yet)
                if not is_today:
                    if len(ins) > len(outs):
                        anomalies.append({
                            "employee": emp.employee_name,
                            "date": date_str,
                            "type": "Missing Punch",
                            "description": _("{0} ENTRADA(s) y {1} SALIDA(s). Falta una SALIDA.").format(len(ins), len(outs)),
                            "severity": "High"
                        })
                    elif len(outs) > len(ins):
                        anomalies.append({
                            "employee": emp.employee_name,
                            "date": date_str,
                            "type": "Missing Punch",
                            "description": _("{0} SALIDA(s) y {1} ENTRADA(s). Falta una ENTRADA.").format(len(outs), len(ins)),
                            "severity": "High"
                        })
                
                # Work on Holiday
                if is_holiday:
                    anomalies.append({
                        "employee": emp.employee_name,
                        "date": date_str,
                        "type": "Work on Holiday",
                        "description": _("Fichaje registrado en día festivo."),
                        "severity": "Medium"
                    })
                
                # Work on Leave
                if leave:
                    anomalies.append({
                        "employee": emp.employee_name,
                        "date": date_str,
                        "type": "Work on Leave",
                        "description": _("Fichaje durante {0}.").format(leave.leave_type),
                        "severity": "Medium"
                    })
                
                # Time Issues (>6h continuous) - Only for completed sessions
                sorted_logs = sorted(logs, key=lambda x: x.time)
                pairs = []
                current_in = None
                
                for log in sorted_logs:
                    if log.log_type == 'IN' and current_in is None:
                        current_in = log.time
                    elif log.log_type == 'OUT' and current_in:
                        pairs.append((current_in, log.time))
                        current_in = None
                
                for p_in, p_out in pairs:
                    session_hours = (p_out - p_in).total_seconds() / 3600.0
                    if session_hours > 6:
                        key = (emp.employee_name, date_str)
                        if key not in flagged_time_issues:
                            flagged_time_issues.add(key)
                            anomalies.append({
                                "employee": emp.employee_name,
                                "date": date_str,
                                "type": "Excessive Continuous Work",
                                "description": _("Sesión continua de {0:.1f}h sin descanso.").format(session_hours),
                                "severity": "High"
                            })
            
            # Attendance-based anomalies
            if att:
                if att.late_entry:
                    anomalies.append({
                        "employee": emp.employee_name,
                        "date": date_str,
                        "type": "Late Entry",
                        "description": _("Llegada tardía") + (f" ({att.in_time})" if att.in_time else ""),
                        "severity": "Low"
                    })
                if att.early_exit:
                    anomalies.append({
                        "employee": emp.employee_name,
                        "date": date_str,
                        "type": "Early Exit",
                        "description": _("Salida anticipada") + (f" ({att.out_time})" if att.out_time else ""),
                        "severity": "Low"
                    })
                if att.status == "Absent" and not leave and not is_holiday:
                    anomalies.append({
                        "employee": emp.employee_name,
                        "date": date_str,
                        "type": "Absent",
                        "description": _("Ausencia sin justificación aprobada."),
                        "severity": "High"
                    })
    
    # 6. Ghost Employees (Job Offer Alta but no checkins)
    for emp_id in ghost_candidates:
        emp = emp_map[emp_id]
        anomalies.append({
            "employee": emp.employee_name,
            "date": get_today(),
            "type": "Ghost Employee",
            "description": _("Job Offer en estado 'Alta' pero sin ningún fichaje registrado."),
            "severity": "Critical"
        })

    return {
        "success": True, 
        "data": anomalies,
        "managers": [{"value": m.name, "label": m.employee_name} for m in managers],
        "is_hr_user": is_hr_user
    }


