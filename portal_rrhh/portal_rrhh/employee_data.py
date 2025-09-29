import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_employees_list(filters=None, limit=20, offset=0):
    """
    Get list of employees for the portal
    """
    try:
        # Default filters
        default_filters = {
            "status": "Active"
        }

        # Merge with provided filters
        if filters:
            if isinstance(filters, str):
                import json
                filters = json.loads(filters)
            default_filters.update(filters)

        # Get employees
        employees = frappe.get_all("Employee",
            filters=default_filters,
            fields=[
                "name",
                "employee_name",
                "employee_id",
                "department",
                "designation",
                "company",
                "user_id",
                "image",
                "status",
                "date_of_joining",
                "cell_number",
                "personal_email",
                "company_email"
            ],
            limit=limit,
            start=offset,
            order_by="employee_name asc"
        )

        # Get total count for pagination
        total_count = frappe.db.count("Employee", default_filters)

        # Format the data
        for employee in employees:
            # Get user email if available
            if employee.get("user_id"):
                user_email = frappe.db.get_value("User", employee["user_id"], "email")
                if user_email:
                    employee["email"] = user_email
                else:
                    employee["email"] = employee.get("company_email") or employee.get("personal_email")
            else:
                employee["email"] = employee.get("company_email") or employee.get("personal_email")

            # Set avatar
            if employee.get("image"):
                employee["avatar"] = employee["image"]
            else:
                employee["avatar"] = "/assets/frappe/images/default-avatar.png"

            # Format date
            if employee.get("date_of_joining"):
                employee["date_of_joining_formatted"] = frappe.utils.formatdate(employee["date_of_joining"])

        return {
            "employees": employees,
            "total_count": total_count,
            "has_more": (offset + len(employees)) < total_count
        }

    except Exception as e:
        frappe.log_error(f"Error getting employees: {str(e)}")
        frappe.throw(_("Error getting employees: {0}").format(str(e)))

@frappe.whitelist(allow_guest=False)
def get_departments_list():
    """
    Get list of departments
    """
    try:
        departments = frappe.get_all("Department",
            fields=["name", "department_name"],
            filters={"is_group": 0},
            order_by="department_name asc"
        )

        return departments

    except Exception as e:
        frappe.log_error(f"Error getting departments: {str(e)}")
        frappe.throw(_("Error getting departments: {0}").format(str(e)))
