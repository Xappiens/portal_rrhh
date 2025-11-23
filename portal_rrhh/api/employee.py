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
    
    # Debug: log filters received (solo valores importantes)
    if filters:
        filter_summary = {k: v for k, v in filters.items() if k in ['provincia', 'company', 'status']}
        frappe.log_error(f"Filtros recibidos: {filter_summary}", "Employee API Debug")

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
            JobOffer.custom_dninie,
            JobOffer.custom_provincia
        )
        .where(JobOffer.custom_dninie.isin(employee_dnis))
    )

    # Apply filters for provincia and company if provided
    if filters:
        if filters.get('provincia'):
            provincia_filter = filters['provincia'].strip() if isinstance(filters['provincia'], str) else str(filters['provincia']).strip()
            if provincia_filter:
                frappe.log_error(f"Filtro provincia: {provincia_filter[:50]}", "Employee API Debug")
                # Como custom_provincia es un Link field, comparamos con el nombre exacto o LIKE
                if isinstance(provincia_filter, list) and provincia_filter[0] == 'like':
                    job_offers_query = job_offers_query.where(JobOffer.custom_provincia.like(provincia_filter[1]))
                else:
                    # Buscar coincidencia exacta o parcial (el Link field almacena el nombre del documento)
                    job_offers_query = job_offers_query.where(JobOffer.custom_provincia.like(f"%{provincia_filter}%"))
        
        if filters.get('company'):
            company_filter = filters['company'].strip() if isinstance(filters['company'], str) else str(filters['company']).strip()
            if company_filter:
                frappe.log_error(f"Filtro empresa: {company_filter[:50]}", "Employee API Debug")
                if isinstance(company_filter, list) and company_filter[0] == 'like':
                    job_offers_query = job_offers_query.where(JobOffer.company.like(company_filter[1]))
                else:
                    job_offers_query = job_offers_query.where(JobOffer.company.like(f"%{company_filter}%"))

    all_job_offers = job_offers_query.run(as_dict=True)
    
    # Debug: log job offers found (solo conteo)
    if filters and (filters.get('provincia') or filters.get('company')):
        frappe.log_error(f"Job Offers con filtros: {len(all_job_offers)}", "Employee API Debug")

    # Group job offers by DNI/NIE for efficient lookup
    job_offers_by_dni = {}
    for jo in all_job_offers:
        dni = jo['custom_dninie']
        if dni not in job_offers_by_dni:
            job_offers_by_dni[dni] = []
        job_offers_by_dni[dni].append(jo)

    # If filters for provincia or company are active, filter employees by matching job offers
    has_job_offer_filters = filters and (filters.get('provincia') or filters.get('company'))
    matching_dnis = set()
    
    if has_job_offer_filters:
        # Get DNI/NIEs that have matching job offers
        matching_dnis = set([jo['custom_dninie'] for jo in all_job_offers if jo.get('custom_dninie')])
        frappe.log_error(f"Filtros activos. JO: {len(all_job_offers)}, DNIs: {len(matching_dnis)}, Empleados antes: {len(employees)}", "Employee API Debug")
    
    # Process each employee with pre-loaded job offers
    filtered_employees = []
    for employee in employees:
        employee_dni = employee.get('custom_dninie')
        
        # If filters for provincia/company are active, only include employees with matching job offers
        if has_job_offer_filters:
            if not employee_dni or employee_dni not in matching_dnis:
                continue
        
        if not employee_dni:
            employee['companies'] = []
            employee['status'] = 'Sin DNI'
            employee['status_text'] = 'Sin DNI'
            filtered_employees.append(employee)
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
        
        filtered_employees.append(employee)
    
    # Debug: log final result
    if has_job_offer_filters:
        frappe.log_error(f"Empleados después de filtrar: {len(filtered_employees)}", "Employee API Debug")

    return filtered_employees

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
