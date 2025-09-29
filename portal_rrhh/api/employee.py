import frappe
from frappe import _

@frappe.whitelist()
def get_employees(filters=None):
    """Get list of employees with essential fields and companies from Job Offers - Optimized version"""
    Employee = frappe.qb.DocType("Employee")
    JobOffer = frappe.qb.DocType("Job Offer")

    # Parse filters if provided
    if filters and isinstance(filters, str):
        import json
        filters = json.loads(filters)

    # Build query with filters
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
    )

    # Apply additional filters
    if filters:
        if filters.get('employee_name'):
            # Handle LIKE filter for employee_name
            if isinstance(filters['employee_name'], list) and filters['employee_name'][0] == 'like':
                query = query.where(Employee.employee_name.like(filters['employee_name'][1]))
            else:
                query = query.where(Employee.employee_name == filters['employee_name'])

        if filters.get('custom_dninie'):
            # Handle LIKE filter for custom_dninie
            if isinstance(filters['custom_dninie'], list) and filters['custom_dninie'][0] == 'like':
                query = query.where(Employee.custom_dninie.like(filters['custom_dninie'][1]))
            else:
                query = query.where(Employee.custom_dninie == filters['custom_dninie'])

    query = query.orderby(Employee.employee_name)
    employees = query.run(as_dict=True)

    # Get all DNIs/NIEs for batch query
    employee_dnis = [emp.get('custom_dninie') for emp in employees if emp.get('custom_dninie')]

    if not employee_dnis:
        # No employees with DNI, set default values
        for employee in employees:
            employee['companies'] = []
            employee['status'] = 'Sin DNI'
            employee['status_text'] = 'Sin DNI'
        return employees

    # Single query to get all job offers for all employees
    job_offers_query = (
        frappe.qb.from_(JobOffer)
        .select(
            JobOffer.company,
            JobOffer.workflow_state,
            JobOffer.custom_dninie
        )
        .where(JobOffer.custom_dninie.isin(employee_dnis))
    )

    all_job_offers = job_offers_query.run(as_dict=True)

    # Group job offers by DNI/NIE for efficient lookup
    job_offers_by_dni = {}
    for jo in all_job_offers:
        dni = jo['custom_dninie']
        if dni not in job_offers_by_dni:
            job_offers_by_dni[dni] = []
        job_offers_by_dni[dni].append(jo)

    # Process each employee with pre-loaded job offers
    for employee in employees:
        employee_dni = employee.get('custom_dninie')
        if not employee_dni:
            employee['companies'] = []
            employee['status'] = 'Sin DNI'
            employee['status_text'] = 'Sin DNI'
            continue

        # Get job offers for this employee from pre-loaded data
        job_offers = job_offers_by_dni.get(employee_dni, [])

        # Extract companies based on workflow state
        alta_companies = list(set([jo['company'] for jo in job_offers if jo['company'] and jo['workflow_state'] == 'Alta']))
        all_companies = list(set([jo['company'] for jo in job_offers if jo['company']]))

        # Determine status and companies to show
        workflow_states = [jo['workflow_state'] for jo in job_offers if jo['workflow_state']]
        if 'Alta' in workflow_states:
            # Tiene Job Offers en "Alta" - mostrar solo empresas de esas Job Offers
            employee['status'] = 'Alta'
            employee['companies'] = alta_companies
            employee['status_text'] = 'De alta en:'
        elif workflow_states:
            # No tiene Job Offers en "Alta" pero tiene Job Offers - mostrar todas las empresas
            employee['status'] = 'Baja'
            employee['companies'] = all_companies
            employee['status_text'] = 'Hojas antiguas en:'
        else:
            # No tiene Job Offers
            employee['status'] = 'Sin Hojas'
            employee['companies'] = []
            employee['status_text'] = 'Sin hojas'

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
