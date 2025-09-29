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
        if not from_date:
            from_date = getdate()
        if not to_date:
            to_date = getdate()

        attendance_records = frappe.get_all("Attendance",
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
        if not frappe.db.exists("Employee", employee):
            return {
                "success": False,
                "message": _("Employee not found")
            }

        employee_info = frappe.get_doc("Employee", employee)

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
