import frappe
from frappe import _
from frappe.utils import now, getdate, get_time
from frappe.model.document import Document

@frappe.whitelist(allow_guest=False)
def mark_attendance(employee, status, attendance_date=None, in_time=None, out_time=None, shift=None):
    """
    Mark attendance for an employee

    Args:
        employee: Employee ID
        status: "Present", "Absent", "Half Day", "Work From Home"
        attendance_date: Date in YYYY-MM-DD format (defaults to today)
        in_time: Time in HH:MM format (optional)
        out_time: Time in HH:MM format (optional)
        shift: Shift name (optional)
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

        attendance.insert(ignore_permissions=True)
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
def get_employee_attendance(employee, from_date=None, to_date=None):
    """
    Get attendance records for an employee

    Args:
        employee: Employee ID
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
    """
    try:
        # Verificar primero que el usuario tenga permisos para ver el empleado
        try:
            employee_doc = frappe.get_doc("Employee", employee)
            if not frappe.has_permission("Employee", "read", employee_doc):
                frappe.throw(_("No tienes permisos para ver este empleado"), frappe.PermissionError)
        except frappe.DoesNotExistError:
            return {
                "success": False,
                "message": _("Employee not found")
            }
        
        if not from_date:
            from_date = getdate()
        if not to_date:
            to_date = getdate()

        # Usar frappe.get_list que respeta permisos automáticamente
        attendance_records = frappe.get_list("Attendance",
            filters={
                "employee": employee,
                "attendance_date": ["between", [from_date, to_date]]
            },
            fields=["name", "attendance_date", "status", "in_time", "out_time", "working_hours", "shift"],
            order_by="attendance_date desc"
        )

        return {
            "success": True,
            "records": attendance_records
        }

    except Exception as e:
        frappe.log_error(f"Error getting attendance: {str(e)}")
        return {
            "success": False,
            "message": _("Error getting attendance: {0}").format(str(e))
        }

@frappe.whitelist(allow_guest=False)
def get_employee_info(employee):
    """
    Get employee information

    Args:
        employee: Employee ID
    """
    try:
        # Usar frappe.get_doc que respeta permisos automáticamente
        try:
            employee_info = frappe.get_doc("Employee", employee)
            # Verificar permisos de lectura
            if not frappe.has_permission("Employee", "read", employee_info):
                frappe.throw(_("No tienes permisos para ver este empleado"), frappe.PermissionError)
        except frappe.DoesNotExistError:
            return {
                "success": False,
                "message": _("Employee not found")
            }

        return {
            "success": True,
            "employee": {
                "name": employee_info.name,
                "employee_name": employee_info.employee_name,
                "employee_id": employee_info.employee_id,
                "department": employee_info.department,
                "designation": employee_info.designation,
                "company": employee_info.company,
                "user_id": employee_info.user_id,
                "image": employee_info.image
            }
        }

    except Exception as e:
        frappe.log_error(f"Error getting employee info: {str(e)}")
        return {
            "success": False,
            "message": _("Error getting employee info: {0}").format(str(e))
        }

@frappe.whitelist(allow_guest=False)
def get_attendance_report(employee, from_date, to_date):
    """
    Get aggregated attendance report for an employee.
    Calculates hours from Employee Checkin and fetches Leave Applications.
    """
    from frappe.utils import getdate, date_diff, add_days, flt
    from datetime import datetime, timedelta

    if not from_date or not to_date:
        return {"success": False, "message": _("Dates are required")}

    from_date = getdate(from_date)
    to_date = getdate(to_date)

    # Validate permissions
    try:
        employee_doc = frappe.get_doc("Employee", employee)
        if not frappe.has_permission("Employee", "read", employee_doc):
             # Also allow if the user is the employee themselves (though has_permission should handle it if set up right)
            if frappe.db.get_value("Employee", employee, "user_id") != frappe.session.user:
                 frappe.throw(_("No permission to view this employee"), frappe.PermissionError)
    except Exception as e:
        return {"success": False, "message": str(e)}

    # 1. Fetch Employee Checkins
    checkins = frappe.get_list("Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", [from_date, to_date + timedelta(days=1)]], # +1 to cover full end date
            "skip_auto_attendance": 0
        },
        fields=["time", "log_type"],
        order_by="time asc"
    )

    # 2. Fetch Leave Applications
    leaves = frappe.get_list("Leave Application",
        filters={
            "employee": employee,
            "status": "Approved",
            "from_date": ["<=", to_date],
            "to_date": [">=", from_date]
        },
        fields=["from_date", "to_date", "leave_type", "half_day", "half_day_date"]
    )

    # 3. Fetch Verified Attendance
    verified_records = frappe.get_list("Verified Attendance",
        filters={
            "employee": employee,
            "attendance_date": ["between", [from_date, to_date]]
        },
        fields=["attendance_date", "total_hours", "verified_in_time", "verified_out_time", "rest_time"]
    )
    verified_map = {d.attendance_date.strftime("%Y-%m-%d"): d for d in verified_records}

    # 3. Process Data
    report_data = {}
    
    # Initialize dates
    days_diff = date_diff(to_date, from_date)
    for i in range(days_diff + 1):
        date_obj = add_days(from_date, i)
        date_str = date_obj.strftime("%Y-%m-%d")
        report_data[date_str] = {
            "date": date_str,
            "hours": 0,
            "status": "",
            "logs": []
        }

    # Process Checkins
    daily_logs = {}
    for log in checkins:
        # Checkin time is datetime
        log_time = log.time
        # Adjust for timezone if needed? usually stored as naive or UTC. Assuming naive server time.
        # Checkins might belong to a shift starting previous day, but for simplicity split by calendar day
        # or rely on shift logic. Here filtering by simple calendar day.
        date_str = log_time.date().strftime("%Y-%m-%d")
        
        if date_str in report_data:
            if date_str not in daily_logs:
                daily_logs[date_str] = []
            daily_logs[date_str].append(log)
            report_data[date_str]['logs'].append({
                "time": log_time.strftime("%H:%M"),
                "type": log.log_type
            })

    # Calculate Hours
    for date_str, logs in daily_logs.items():
        # Simple logic: Sort by time. OUT - IN.
        # If multiple pairs, sum them.
        # If sequence is IN, IN, OUT -> assume first IN starts, OUT ends. 
        # Robust logic: First IN, Last OUT? Or pairs.
        # Using First IN and Last OUT is common for total duration.
        # Using Pairs is better for breaks.
        # Let's try pairs: IN..OUT, IN..OUT.
        
        total_seconds = 0
        last_in = None
        
        for log in logs:
            if log.log_type == 'IN':
                if last_in is None:
                    last_in = log.time
            elif log.log_type == 'OUT':
                if last_in:
                    # Pair found
                    diff = (log.time - last_in).total_seconds()
                    total_seconds += diff
                    last_in = None
        
        # If user forgot to punch OUT, or IN, this logic might undercount. 
        # But without OUT, we can't calculate duration.
        # Optional: If only one IN and one OUT (First and Last), use that?
        # Let's stick to pairs for now as it's safer for breaks.
        
        # Fallback: if total_seconds is 0 but we have logs, maybe just subtract last - first?
        # Provide both or stick to one. "Valid Pairs" is stricter. 
        # Let's stick to strict pairs to encourage correct punching. 
        
        hours = total_seconds / 3600.0
        report_data[date_str]['hours'] = flt(hours, 2)
        report_data[date_str]['rest_time'] = "Not Calc" # Placeholder, computed in Vue usually or we can compute here too if needed, but Vue does it well.

    # Merge Verified Data
    for date_str, verified in verified_map.items():
        if date_str in report_data:
            report_data[date_str]['hours'] = verified.total_hours
            report_data[date_str]['is_verified'] = True
            report_data[date_str]['verified_id'] = verified.name
            
            # Override Logs for display if times provided
            if verified.verified_in_time or verified.verified_out_time:
                # Clear existing logs visually or just prepend/replace ? 
                # Request says "mostrará la información del registro verificado"
                # So best to construct a fake log list or special fields
                new_logs = []
                if verified.verified_in_time:
                    # Time object to string or check logs format? logs use datetime objects usually
                    # But frontend expects {time: "HH:MM", type: "IN"}
                    # verified_in_time is timedelta usually from get_list or Time
                    v_in = str(verified.verified_in_time) # Ensure string HH:MM:SS
                    if len(v_in) > 5: v_in = v_in[:5]
                    new_logs.append({"time": v_in, "type": "IN"})
                
                if verified.verified_out_time:
                    v_out = str(verified.verified_out_time)
                    if len(v_out) > 5: v_out = v_out[:5]
                    new_logs.append({"time": v_out, "type": "OUT"})
                
                # If we have verified times, use them. If not, keep calculated logs? 
                # Usually if verifying hours, you verify the times too.
                # If only hours verified but no times, we show hours but maybe keep logs blank or original?
                # "mostrará la información del registro verificado" -> implies show verified data.
                if new_logs:
                    report_data[date_str]['logs'] = new_logs # Replace logs with verified ones
            
            if verified.rest_time:
                report_data[date_str]['verified_rest_time'] = verified.rest_time

    # Process Leaves
    for leave in leaves:
        l_from = leave.from_date
        l_to = leave.to_date
        # Clamp to requested range
        start = max(l_from, from_date)
        end = min(l_to, to_date)
        
        l_diff = date_diff(end, start)
        for i in range(l_diff + 1):
            d = add_days(start, i)
            d_str = d.strftime("%Y-%m-%d")
            
            if d_str in report_data:
                # Handle Half Day
                is_half = leave.half_day and (leave.half_day_date == d or not leave.half_day_date)
                note = f"{leave.leave_type}" + (" (Half Day)" if is_half else "")
                
                if report_data[d_str]['status']:
                    report_data[d_str]['status'] += ", " + note
                else:
                    report_data[d_str]['status'] = note

    return {
        "success": True,
        "data": list(report_data.values())
    }

@frappe.whitelist(allow_guest=False)
def export_attendance_report(employee, from_date, to_date):
    """
    Export attendance report to Excel
    """
    from frappe.utils.xlsxutils import build_xlsx_response
    
    # 1. Get Data
    result = get_attendance_report(employee, from_date, to_date)
    
    if not result.get("success"):
        frappe.throw(result.get("message") or _("Error generating report"))
        
    data = result.get("data", [])
    
    employee_name = frappe.db.get_value("Employee", employee, "employee_name") or employee
    
    # 2. Build Headers
    headers = [
        _("Fecha"),
        _("Empleado"),
        _("Hora Entrada"),
        _("Hora Salida"),
        _("Tiempo Descanso"),
        _("Total Horas")
    ]
    
    xlsx_data = [headers]
    
    # 3. Build Rows
    for row in data:
        # helpers
        def get_in(logs):
            if not logs: return '-'
            ins = [l for l in logs if l.get('type') == 'IN']
            if not ins: return 'Usuario no registró hora de entrada'
            return ins[0].get('time')
            
        def get_out(logs):
            if not logs: return '-'
            outs = [l for l in logs if l.get('type') == 'OUT']
            if not outs: return 'Usuario no registró hora de salida'
            return outs[-1].get('time')

        # Logic matches Vue implementation roughly for display
        
        in_time = get_in(row.get('logs', []))
        out_time = get_out(row.get('logs', []))
        
        # Override with verified if available (logic from get_attendance_report handles merging verified times into logs usually, 
        # but let's be safe and check if our previous logic did that successfully.
        # Looking at get_attendance_report: 
        # if verified.verified_in_time: logs are replaced. So get_in/out on logs should work.
        
        # Determine Rest Time
        rest_time = row.get('verified_rest_time') or '-'
        # If not verified rest, we could calc it, but let's keep it simple for now or calc it?
        # Vue does `calculateRestTime`. Let's assume user cares mostly about verified or just raw stamps.
        # Implementing a simple calc for python if needed:
        if rest_time == '-' and len(row.get('logs', [])) >= 2:
             # Implement simple calc for python
             logs = row.get('logs', [])
             ifLogs = len(logs)
             total_minutes = 0
             # Sort just in case, though usually sorted
             # logs are dicts: {'time': 'HH:MM', 'type': 'IN'/'OUT'}
             # Convert to timedeltas for math? or datetime
             # We need a reference date or just hours
             
             from datetime import datetime
             
             for i in range(len(logs) - 1):
                 curr = logs[i]
                 next_l = logs[i+1]
                 
                 if curr.get('type') == 'OUT' and next_l.get('type') == 'IN':
                    try:
                        # Parse HH:MM
                        t1 = datetime.strptime(curr.get('time'), "%H:%M")
                        t2 = datetime.strptime(next_l.get('time'), "%H:%M")
                        
                        diff_seconds = (t2 - t1).total_seconds()
                        if diff_seconds > 0:
                            total_minutes += (diff_seconds / 60)
                    except:
                        pass
             
             if total_minutes > 0:
                 h = int(total_minutes // 60)
                 m = int(round(total_minutes % 60))
                 rest_time = f"{h:02d}:{m:02d}"
        
        # Parse legacy verified rest time if needed
        import re
        if rest_time and 'h' in rest_time:
            match = re.match(r'(\d+)h\s*(\d+)m', rest_time)
            if match:
                h = int(match.group(1))
                m = int(match.group(2))
                rest_time = f"{h:02d}:{m:02d}"

        # Format Hours to HH:MM
        hours_val = row.get('hours') or 0
        h_val = int(hours_val)
        m_val = int(round((hours_val - h_val) * 60))
        hours_formatted = f"{h_val:02d}:{m_val:02d}"

        xlsx_row = [
            row.get('date'),
            employee_name,
            in_time,
            out_time,
            rest_time,
            hours_formatted
        ]
        xlsx_data.append(xlsx_row)

    # 4. Return Response
    from frappe.utils import now_datetime
    xlsx_data.append([])
    xlsx_data.append([_("Información extraída del Portal RRHH el día {0}").format(now_datetime().strftime("%d/%m/%Y %H:%M"))])
    
    filename = f"Reporte_Asistencia_{employee_name}_{from_date}_{to_date}.xlsx"
    build_xlsx_response(xlsx_data, filename)

@frappe.whitelist(allow_guest=False)
def save_verified_attendance(employee, date, total_hours, in_time=None, out_time=None, rest_time=None):
    """
    Creates or updates a Verified Attendance record.
    """
    if not frappe.has_permission("Verified Attendance", "write"):
         # Check specific role if has_permission fails for some reason (e.g. creating new doc checks 'create')
         # But standard permission check should suffice.
         # Double check 'System Manager' or 'HR Manager'
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
    
    frappe.errprint(f"DEBUG: Verifying Attendance. ID: {doc_name}")
    
    try:
        # Elevate to Administrator
        frappe.set_user("Administrator")
        
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
            doc.owner = current_user
            is_new = True

        # 3. Set Values
        doc.total_hours = total_hours
        if in_time: doc.verified_in_time = in_time
        if out_time: doc.verified_out_time = out_time
        if rest_time: doc.rest_time = rest_time
        
        # 4. Save with Race Condition Protection
        try:
            if is_new:
                doc.company = frappe.db.get_value("Employee", emp_clean, "company") # ensure company is set
                doc.insert(ignore_permissions=True)
            else:
                doc.save(ignore_permissions=True)
                
        except frappe.DuplicateEntryError:
            # Race condition or 'exists' lied. Reload and Update.
            frappe.errprint("DEBUG: Race condition caught. Updating existing.")
            doc = frappe.get_doc("Verified Attendance", doc_name)
            doc.total_hours = total_hours
            if in_time: doc.verified_in_time = in_time
            if out_time: doc.verified_out_time = out_time
            if rest_time: doc.rest_time = rest_time
            doc.save(ignore_permissions=True)
            
        frappe.errprint(f"DEBUG: Saved successfully: {doc.name}")
        
        return {"success": True, "message": _("Attendance Verified")}

    except Exception as e:
        frappe.log_error(title="Attendance Verify Error", message=str(e))
        return {"success": False, "message": str(e)}
    
    finally:
        # Always restore user
        frappe.set_user(current_user)

@frappe.whitelist(allow_guest=False)
def get_attendance_anomalies(from_date, to_date, employee=None):
    """
    Detect anomalies in attendance:
    - Missing Punches (IN without OUT, etc)
    - Late Entry / Early Exit
    - Absent
    - Work on Holiday / Leave
    """
    from frappe.utils import getdate, add_days, date_diff, cint, today
    from datetime import timedelta
    
    if not from_date or not to_date:
        return {"success": False, "message": _("Dates are required")}
        
    start_date = getdate(from_date)
    end_date = getdate(to_date)
    
    # 1. Scope Users
    filters = {"status": "Active"}
    if employee:
        filters["name"] = employee
        
    # Permission check is implicit in get_list if not ignore_permissions
    # But for a dashboard, we might want to ensure HR managers see all.
    employees = frappe.get_list("Employee", 
        filters=filters, 
        fields=["name", "employee_name", "department", "company", "holiday_list", "job_applicant", "status", "date_of_joining"]
    )
    emp_map = {e.name: e for e in employees}
    emp_ids = list(emp_map.keys())
    
    if not emp_ids:
         return {"success": True, "data": []}

    # Pre-fetch Job Offers for "Ghost Employee" check
    # Ghost Employee: Active Employee, has Job Offer 'Accepted', NO checkins ever (or in a relevant period?)
    # User said: "que no tienen registros en employee checkin". 
    # Let's interpret as: Employees who supposedly started (Job Offer Accepted) but haven't punched.
    # We will check if they have ANY checkins. 
    # Optimization: Fetch list of employees who HAVE checkins. The rest are potentially ghosts.
    
    employees_with_checkins = frappe.get_all("Employee Checkin", fields=["employee"], distinct=True, pluck="employee")
    employees_with_checkins_set = set(employees_with_checkins)

    # Job Offers map: Job Applicant -> Job Offer
    job_applicants = [e.job_applicant for e in employees if e.job_applicant]
    job_offer_map = {}
    if job_applicants:
        # Assuming "Alta" means "Accepted"
        offers = frappe.get_list("Job Offer", 
            filters={"job_applicant": ["in", job_applicants], "status": "Accepted"},
            fields=["job_applicant", "status"]
        )
        for o in offers:
            job_offer_map[o.job_applicant] = o

    # 2. Fetch Data in Bulk for Range
    
    # Checkins
    checkins = frappe.get_list("Employee Checkin",
        filters={
            "employee": ["in", emp_ids],
            "time": ["between", [start_date, end_date + timedelta(days=1)]],
            "skip_auto_attendance": 0
        },
        fields=["employee", "time", "log_type", "device_id"],
        order_by="time asc"
    )
    
    # Attendance
    attendances = frappe.get_list("Attendance",
        filters={
            "employee": ["in", emp_ids],
            "attendance_date": ["between", [start_date, end_date]]
        },
        fields=["employee", "attendance_date", "status", "late_entry", "early_exit", "in_time", "out_time"]
    )
    
    # Leaves
    leaves = frappe.get_list("Leave Application",
        filters={
            "employee": ["in", emp_ids],
            "status": "Approved",
            "from_date": ["<=", end_date],
            "to_date": [">=", start_date]
        },
        fields=["employee", "from_date", "to_date", "leave_type"]
    )
    
    # Holidays
    # We need to check holidays for each employee's holiday list.
    # Group employees by holiday list to minimize queries
    holiday_lists = set(e.holiday_list for e in employees if e.holiday_list)
    holidays_map = {} # {holiday_list_name: [dates]}
    
    if holiday_lists:
        h_records = frappe.get_list("Holiday",
            filters={
                "parent": ["in", list(holiday_lists)],
                "holiday_date": ["between", [start_date, end_date]]
            },
            fields=["parent", "holiday_date"]
        )
        for h in h_records:
            if h.parent not in holidays_map:
                holidays_map[h.parent] = set()
            holidays_map[h.parent].add(h.holiday_date)

    # 3. Process Logic
    anomalies = []
    
    # Organize data by Employee -> Date
    data_map = {} # {emp: {date: {checkins: [], attendance: None, leave: None}}}
    
    for e in emp_ids:
        data_map[e] = {}
        
    for c in checkins:
        d = c.time.date().strftime("%Y-%m-%d")
        if d not in data_map[c.employee]: data_map[c.employee][d] = {"checkins": [], "attendance": None, "leave": None}
        data_map[c.employee][d]["checkins"].append(c)
        
    for a in attendances:
        d = a.attendance_date.strftime("%Y-%m-%d")
        if d not in data_map[a.employee]: data_map[a.employee][d] = {"checkins": [], "attendance": None, "leave": None}
        data_map[a.employee][d]["attendance"] = a
        
    for l in leaves:
        # Expand leave range
        l_start = max(l.from_date, start_date)
        l_end = min(l.to_date, end_date)
        days = date_diff(l_end, l_start)
        for i in range(days + 1):
            d = add_days(l_start, i).strftime("%Y-%m-%d")
            if d in data_map[l.employee] or (not employee): # only care if data exists or we iterating all days?
                 # Actually we should iterate all days if we want to find "Absent without leave" etc.
                 # But let's stick to "Unusual situations based on existing data" or missing punches.
                 if d not in data_map[l.employee]: data_map[l.employee][d] = {"checkins": [], "attendance": None}
                 data_map[l.employee][d]["leave"] = l

    # Iterate findings
    for emp_id, days_data in data_map.items():
        emp_obj = emp_map[emp_id]
        
        for date_str, info in days_data.items():
            date_obj = getdate(date_str)
            logs = info.get("checkins", [])
            att = info.get("attendance")
            leave = info.get("leave")
            
            # Check Holiday
            is_holiday = False
            if emp_obj.holiday_list and emp_obj.holiday_list in holidays_map:
                if date_obj in holidays_map[emp_obj.holiday_list]:
                    is_holiday = True
            
            # 1. Missing Punches (Logs exist but no pairs or odd count)
            # Simple check: If logs exist, first must be IN, last must be OUT (if on same day).
            # Strict check: Every IN needs an OUT.
            if logs:
                ins = [l for l in logs if l.log_type == 'IN']
                outs = [l for l in logs if l.log_type == 'OUT']
                
                # Check 1: Missing OUT for an IN
                if len(ins) > len(outs):
                    anomalies.append({
                        "employee": emp_obj.employee_name,
                        "date": date_str,
                        "type": "Missing Punch",
                        "description": _("El usuario tiene {0} registros de ENTRADA y {1} de SALIDA. Probablemente falta una SALIDA.").format(len(ins), len(outs)),
                        "severity": "High"
                    })
                elif len(outs) > len(ins):
                     anomalies.append({
                        "employee": emp_obj.employee_name,
                        "date": date_str,
                        "type": "Missing Punch",
                        "description": _("El usuario tiene {0} registros de SALIDA y {1} de ENTRADA. Probablemente falta una ENTRADA.").format(len(outs), len(ins)),
                        "severity": "High"
                    })
                
                # Check 2: Work on Holiday
                if is_holiday:
                     anomalies.append({
                        "employee": emp_obj.employee_name,
                        "date": date_str,
                        "type": "Work on Holiday",
                        "description": _("El usuario fichó en un día festivo."),
                        "severity": "Medium"
                    })
                
                # Check 3: Work on Leave
                if leave:
                     anomalies.append({
                        "employee": emp_obj.employee_name,
                        "date": date_str,
                        "type": "Work on Leave",
                        "description": _("El usuario fichó durante {0}.").format(leave.leave_type),
                        "severity": "Medium"
                    })
            
            # 2. Processed Attendance Anomalies
            if att:
                if att.late_entry:
                     anomalies.append({
                        "employee": emp_obj.employee_name,
                        "date": date_str,
                        "type": "Late Entry",
                        "description": _("El empleado llegó tarde.") + (f" ({att.in_time})" if att.in_time else ""),
                        "severity": "Low"
                    })
                if att.early_exit:
                     anomalies.append({
                        "employee": emp_obj.employee_name,
                        "date": date_str,
                        "type": "Early Exit",
                        "description": _("El empleado salió temprano.") + (f" ({att.out_time})" if att.out_time else ""),
                        "severity": "Low"
                    })
                if att.status == "Absent" and not leave and not is_holiday:
                     anomalies.append({
                        "employee": emp_obj.employee_name,
                        "date": date_str,
                        "type": "Absent",
                        "description": _("Marcado como Ausente sin solicitud de ausencia aprobada."),
                        "severity": "High"
                    })
            
            # 3. Time Anomalies ( > 6 hours logic)
            if logs:
                # Need pairs to calculate duration
                # Sort logs
                sorted_logs = sorted(logs, key=lambda x: x.time)
                pairs = []
                current_in = None
                
                for log in sorted_logs:
                    if log.log_type == 'IN':
                        if current_in is None:
                            current_in = log.time
                    elif log.log_type == 'OUT':
                        if current_in:
                            pairs.append((current_in, log.time))
                            current_in = None
                
                # Check A: Single session > 6 hours
                for p_in, p_out in pairs:
                    session_duration = (p_out - p_in).total_seconds() / 3600.0
                    if session_duration > 6:
                         anomalies.append({
                            "employee": emp_obj.employee_name,
                            "date": date_str,
                            "type": "Excessive Continuous Work",
                            "description": _("Sesión de trabajo continua de {0:.2f} horas (más de 6h sin descanso).").format(session_duration),
                            "severity": "High"
                        })

                # Check B: Total work > 6 hours AND No Break (Only 1 pair)
                # If they have > 6h total BUT only 1 session, implies they didn't clock out for break.
                # (This overlaps with Check A effectively, as >6h diff in 1 pair is >6h session)
                # But user asked specifically: "Empleados que trabajan más de 6 horas y no hacen decanso."
                # Usually this means: Total Hours > 6 AND Number of Sessions == 1.
                
                total_hours = sum([(p[1] - p[0]).total_seconds() for p in pairs]) / 3600.0
                if total_hours > 6 and len(pairs) == 1:
                    # Avoid duplicate if we already flagged "Excessive Continuous Work" for the same reason?
                    # The user might want distinct categories. "Excessive Continuous Work" is basically "No Break".
                    # Let's flag it as "No Break" if not already flagged.
                    already_flagged = any(a['type'] == 'Excessive Continuous Work' and a['date'] == date_str and a['employee'] == emp_obj.employee_name for a in anomalies)
                    if not already_flagged:
                         anomalies.append({
                            "employee": emp_obj.employee_name,
                            "date": date_str,
                            "type": "No Break",
                            "description": _("Trabajó {0:.2f} horas sin registrar un descanso (sesión única).").format(total_hours),
                            "severity": "Medium"
                        })
            
            # 4. Ghost Employee Check (Per Date? No, it's a global state mostly, but we report it per query)
            # Logic: If query covers "Today" or relevant period, and they are Active + Job Offer Accepted + No Checkins EVER.
            # Use data_map or global set? global set `employees_with_checkins_set`.
            # Only report once per employee, not every day.
            
    # Ghost Employee Check (Global for the list of employees)
    for emp_id in emp_ids:
        emp = emp_map[emp_id]
        # Check Job Offer Accepted
        if emp.job_applicant and emp.job_applicant in job_offer_map:
            # Check Checkins
            if emp.name not in employees_with_checkins_set:
                # Verify they are Active (already filtered by Active)
                # Verify Date of Joining? If joined years ago and no checkins? Likely old data or bug.
                # If joined recently? Ghost.
                # Just report it.
                anomalies.append({
                    "employee": emp.employee_name,
                    "date": today(), # Report as "Today" or just generic
                    "type": "Ghost Employee",
                    "description": _("El empleado tiene una Oferta de Trabajo Aceptada pero NINGÚN registro de fichaje histórico."),
                    "severity": "Critical"
                })

    return {"success": True, "data": anomalies}


