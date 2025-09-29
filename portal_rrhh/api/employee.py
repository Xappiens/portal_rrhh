import frappe
from frappe import _

@frappe.whitelist()
def get_employees():
    """Get list of employees with essential fields and companies from Job Offers"""
    Employee = frappe.qb.DocType("Employee")
    JobOffer = frappe.qb.DocType("Job Offer")

    # Get employees with basic info
    query = (
        frappe.qb.from_(Employee)
        .select(
            Employee.name,
            Employee.employee_name,
            Employee.company,
            Employee.department,
            Employee.designation,
            Employee.reports_to,
            Employee.status,
            Employee.date_of_joining,
            Employee.employee_number,
            Employee.cell_number,
            Employee.personal_email,
            Employee.company_email,
            Employee.custom_dninie,
            Employee.custom_no_seguridad_social,
            Employee.image
        )
        .where(Employee.status == "Active")
        .orderby(Employee.employee_name)
    )

    employees = query.run(as_dict=True)

    # For each employee, get companies from Job Offers with workflow_state = 'Alta'
    for employee in employees:
        # Get companies from Job Offers where job_applicant matches employee's email
        job_offers_query = (
            frappe.qb.from_(JobOffer)
            .select(JobOffer.company)
            .where(
                (JobOffer.job_applicant == employee.company_email) &
                (JobOffer.workflow_state == "Alta")
            )
            .distinct()
        )

        companies = job_offers_query.run(as_dict=True)
        employee.companies = [comp.company for comp in companies] if companies else [employee.company]

    return employees

@frappe.whitelist()
def get_employee(name):
    """Get specific employee details"""
    Employee = frappe.qb.DocType("Employee")

    query = (
        frappe.qb.from_(Employee)
        .select("*")
        .where(Employee.name == name)
        .limit(1)
    )

    employee = query.run(as_dict=True)
    if not len(employee):
        frappe.throw(_("Employee not found"), frappe.DoesNotExistError)

    return employee[0]
