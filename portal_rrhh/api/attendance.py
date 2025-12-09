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
