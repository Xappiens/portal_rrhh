import frappe
from frappe import _

def filter_by_permissions(documents, doctype):
    """Filtra documentos según los permisos del usuario"""
    if not documents:
        return []
    
    filtered = []
    for doc in documents:
        doc_name = doc.get('name') if isinstance(doc, dict) else doc
        try:
            # Verificar permisos de lectura usando frappe.get_doc con ignore_permissions=False
            # Esto respeta automáticamente los permisos de usuario y roles
            if frappe.has_permission(doctype, "read", doc_name if isinstance(doc_name, str) else doc):
                filtered.append(doc)
        except frappe.PermissionError:
            # Si no tiene permisos, omitir el documento
            continue
        except Exception:
            # Si hay algún error, verificar usando get_doc_permissions
            try:
                doc_obj = frappe.get_doc(doctype, doc_name) if isinstance(doc_name, str) else doc
                perms = frappe.permissions.get_doc_permissions(doc_obj)
                if perms.get("read"):
                    filtered.append(doc)
            except:
                continue
    
    return filtered

@frappe.whitelist()
def get_employees(filters=None):
    """Get list of employees with essential fields and companies from Job Offers - Optimized version"""
    # Parse filters if provided
    if filters and isinstance(filters, str):
        import json
        filters = json.loads(filters)

    # Usar frappe.get_list para respetar permisos automáticamente
    filters_dict = {"status": "Active"}
    
    # Aplicar filtros adicionales
    if filters:
        if filters.get('employee_name'):
            if isinstance(filters['employee_name'], list) and filters['employee_name'][0] == 'like':
                filters_dict['employee_name'] = filters['employee_name']
            else:
                filters_dict['employee_name'] = filters['employee_name']
        
        if filters.get('custom_dninie'):
            if isinstance(filters['custom_dninie'], list) and filters['custom_dninie'][0] == 'like':
                filters_dict['custom_dninie'] = filters['custom_dninie']
            else:
                filters_dict['custom_dninie'] = filters['custom_dninie']

    # Verificar primero si el usuario tiene permisos de lectura en Employee
    try:
        meta = frappe.get_meta("Employee")
        role_permissions = frappe.permissions.get_role_permissions(meta, user=frappe.session.user)
        if not role_permissions.get("read") and not role_permissions.get("select"):
            # No tiene permisos básicos de lectura, devolver lista vacía
            return []
    except Exception:
        # Si hay error verificando permisos, continuar pero filtrar después
        pass

    # Obtener empleados usando frappe.get_list que respeta permisos automáticamente
    employees = frappe.get_list(
        "Employee",
        fields=[
            "name",
            "employee_name",
            "company",
            "department",
            "designation",
            "reports_to",
            "status",
            "date_of_joining",
            "employee_number",
            "cell_number",
            "personal_email",
            "company_email",
            "custom_dninie",
            "custom_no_seguridad_social",
            "image"
        ],
        filters=filters_dict,
        order_by="employee_name asc"
    )

    # Filtrar adicionalmente por permisos específicos de cada documento
    filtered_employees = []
    for emp in employees:
        try:
            # Verificar permisos de lectura específicos para este empleado
            if frappe.has_permission("Employee", "read", emp.get('name')):
                filtered_employees.append(emp)
        except (frappe.PermissionError, frappe.DoesNotExistError):
            # Si no tiene permisos o el documento no existe, omitir
            continue
        except Exception:
            # Si hay algún error, verificar usando get_doc_permissions
            try:
                emp_doc = frappe.get_doc("Employee", emp.get('name'))
                perms = frappe.permissions.get_doc_permissions(emp_doc)
                if perms.get("read"):
                    filtered_employees.append(emp)
            except:
                continue
    
    employees = filtered_employees

    # Get all DNIs/NIEs for batch query
    employee_dnis = [emp.get('custom_dninie') for emp in employees if emp.get('custom_dninie')]

    if not employee_dnis:
        # No employees with DNI, set default values
        for employee in employees:
            employee['companies'] = []
            employee['status'] = 'Sin DNI'
            employee['status_text'] = 'Sin DNI'
        return employees

    # Obtener job offers usando frappe.get_list para respetar permisos
    job_offer_filters = {"custom_dninie": ["in", employee_dnis]}
    
    # Aplicar filtros para provincia y company si se proporcionan
    if filters:
        if filters.get('provincia'):
            provincia_filter = filters['provincia'].strip() if isinstance(filters['provincia'], str) else str(filters['provincia']).strip()
            if provincia_filter:
                if isinstance(provincia_filter, list) and provincia_filter[0] == 'like':
                    job_offer_filters['custom_provincia'] = provincia_filter
                else:
                    job_offer_filters['custom_provincia'] = ["like", f"%{provincia_filter}%"]
        
        if filters.get('company'):
            company_filter = filters['company'].strip() if isinstance(filters['company'], str) else str(filters['company']).strip()
            if company_filter:
                if isinstance(company_filter, list) and company_filter[0] == 'like':
                    job_offer_filters['company'] = company_filter
                else:
                    job_offer_filters['company'] = ["like", f"%{company_filter}%"]

    all_job_offers = frappe.get_list(
        "Job Offer",
        fields=["company", "workflow_state", "custom_dninie", "custom_provincia"],
        filters=job_offer_filters
    )

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

    return filtered_employees

@frappe.whitelist()
def get_employee(name):
    """Get specific employee details"""
    # Usar frappe.get_doc que respeta permisos automáticamente
    try:
        employee = frappe.get_doc("Employee", name)
        # Verificar permisos de lectura
        if not frappe.has_permission("Employee", "read", employee):
            frappe.throw(_("No tienes permisos para ver este empleado"), frappe.PermissionError)
        return employee.as_dict()
    except frappe.DoesNotExistError:
        frappe.throw(_("Employee not found"), frappe.DoesNotExistError)
