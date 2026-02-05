import frappe
from frappe import _
from frappe.utils import getdate, formatdate


@frappe.whitelist()
def get_incentives(filters=None, limit=None, offset=None):
    """Obtener lista de incentivos de empleados con filtros
    
    Args:
        filters: JSON string con criterios de filtrado
        limit: Número máximo de registros a retornar
        offset: Número de registros a omitir
    
    Returns:
        dict con 'data' (lista de incentivos) y 'total' (total para paginación)
    """
    import json as json_lib
    
    # Parse filters if provided
    if filters and isinstance(filters, str):
        filters = json_lib.loads(filters)
    
    # Parse pagination params
    limit_start = int(offset) if offset else 0
    page_length = int(limit) if limit else None
    
    # Construir filtros
    filters_dict = {}
    or_filters = []
    
    if filters:
        # Filtro por empleado
        if filters.get('employee'):
            filters_dict['employee'] = filters['employee']
        
        # Filtro por fecha de nómina (rango)
        if filters.get('payroll_date_from'):
            filters_dict['payroll_date'] = ['>=', filters['payroll_date_from']]
        if filters.get('payroll_date_to'):
            if 'payroll_date' in filters_dict:
                # Ya existe un filtro, necesitamos combinar
                filters_dict['payroll_date'] = [
                    'between',
                    filters.get('payroll_date_from', '1900-01-01'),
                    filters.get('payroll_date_to', '2100-12-31')
                ]
            else:
                filters_dict['payroll_date'] = ['<=', filters['payroll_date_to']]
        
        # Filtro por estado (docstatus)
        if filters.get('status'):
            if filters['status'] == 'Draft':
                filters_dict['docstatus'] = 0
            elif filters['status'] == 'Submitted':
                filters_dict['docstatus'] = 1
            elif filters['status'] == 'Cancelled':
                filters_dict['docstatus'] = 2
        
        # Filtro por componente salarial
        if filters.get('salary_component'):
            filters_dict['salary_component'] = filters['salary_component']
        
        # Filtro por compañía
        if filters.get('company'):
            filters_dict['company'] = filters['company']
        
        # Filtro por provincia
        if filters.get('custom_provincia'):
            filters_dict['custom_provincia'] = filters['custom_provincia']
        
        # Búsqueda de texto (nombre de empleado, ID de incentivo)
        if filters.get('search_text'):
            search_text = f"%{filters['search_text']}%"
            or_filters = [
                ['employee_name', 'like', search_text],
                ['name', 'like', search_text],
                ['employee', 'like', search_text]
            ]
    
    # Obtener total count
    if or_filters:
        count_result = frappe.get_list(
            "Employee Incentive",
            filters=filters_dict,
            or_filters=or_filters,
            fields=["count(name) as total"],
            as_list=True
        )
        total_count = count_result[0][0] if count_result else 0
    else:
        total_count = frappe.db.count("Employee Incentive", filters=filters_dict)
    
    # Obtener incentivos usando frappe.get_list que respeta permisos
    list_kwargs = {
        "fields": [
            "name",
            "employee",
            "employee_name",
            "company",
            "department",
            "salary_component",
            "currency",
            "payroll_date",
            "incentive_amount",
            "custom_provincia",
            "custom_incentivo_aprobado_por",
            "custom_justificación",
            "custom_by_hours",
            "custom_incentive_hours",
            "docstatus",
            "workflow_state",
            "creation",
            "modified",
            "modified_by"
        ],
        "filters": filters_dict,
        "order_by": "modified desc"
    }
    
    if or_filters:
        list_kwargs["or_filters"] = or_filters
    
    if page_length:
        list_kwargs["limit_start"] = limit_start
        list_kwargs["limit_page_length"] = page_length
    
    incentives = frappe.get_list("Employee Incentive", **list_kwargs)
    
    # Formatear datos para el frontend
    for incentive in incentives:
        # Estado del documento
        if incentive.get('docstatus') == 0:
            incentive['status'] = 'Draft'
            incentive['status_label'] = 'Borrador'
        elif incentive.get('docstatus') == 1:
            incentive['status'] = 'Submitted'
            incentive['status_label'] = 'Enviado'
        elif incentive.get('docstatus') == 2:
            incentive['status'] = 'Cancelled'
            incentive['status_label'] = 'Cancelado'
        
        # Formatear fecha
        if incentive.get('payroll_date'):
            incentive['payroll_date_formatted'] = formatdate(incentive['payroll_date'], 'dd MMM yyyy')
        
        # Formatear monto
        if incentive.get('incentive_amount'):
            incentive['incentive_amount_formatted'] = f"{incentive['incentive_amount']:.2f}"
    
    return {"data": incentives, "total": total_count}


@frappe.whitelist()
def get_incentive_details(incentive_name):
    """Obtener detalles completos de un incentivo específico"""
    try:
        incentive = frappe.get_doc("Employee Incentive", incentive_name)
        
        # Verificar permisos
        if not frappe.has_permission("Employee Incentive", "read", incentive):
            frappe.throw(_("No tienes permisos para ver este incentivo"), frappe.PermissionError)
        
        return incentive.as_dict()
    except frappe.DoesNotExistError:
        frappe.throw(_("Incentivo no encontrado"), frappe.DoesNotExistError)
    except Exception as e:
        frappe.log_error(f"Error en get_incentive_details: {str(e)}", "Incentive API Error")
        frappe.throw(_("Error al obtener detalles del incentivo"))


@frappe.whitelist()
def get_salary_components(company=None):
    """Obtener lista de componentes salariales de tipo 'earning' con custom_is_incentive=1"""
    filters = {
        "type": "earning",
        "custom_is_incentive": 1
    }
    
    if company:
        filters["company"] = company
    
    components = frappe.get_list(
        "Salary Component",
        fields=["name", "salary_component", "company"],
        filters=filters,
        order_by="salary_component asc"
    )
    
    return components


@frappe.whitelist()
def get_incentive_stats(filters=None):
    """Obtener estadísticas de incentivos"""
    import json as json_lib
    
    if filters and isinstance(filters, str):
        filters = json_lib.loads(filters)
    
    filters_dict = {}
    if filters:
        if filters.get('payroll_date_from'):
            filters_dict['payroll_date'] = ['>=', filters['payroll_date_from']]
        if filters.get('payroll_date_to'):
            if 'payroll_date' in filters_dict:
                filters_dict['payroll_date'] = [
                    'between',
                    filters.get('payroll_date_from', '1900-01-01'),
                    filters.get('payroll_date_to', '2100-12-31')
                ]
            else:
                filters_dict['payroll_date'] = ['<=', filters['payroll_date_to']]
    
    # Total de incentivos
    total_count = frappe.db.count("Employee Incentive", filters=filters_dict)
    
    # Total enviados
    submitted_filters = filters_dict.copy()
    submitted_filters['docstatus'] = 1
    submitted_count = frappe.db.count("Employee Incentive", filters=submitted_filters)
    
    # Total borradores
    draft_filters = filters_dict.copy()
    draft_filters['docstatus'] = 0
    draft_count = frappe.db.count("Employee Incentive", filters=draft_filters)
    
    # Suma total de montos (solo enviados)
    total_amount = frappe.db.sql("""
        SELECT SUM(incentive_amount) 
        FROM `tabEmployee Incentive`
        WHERE docstatus = 1
    """, as_dict=False)
    
    total_amount_value = total_amount[0][0] if total_amount and total_amount[0][0] else 0
    
    return {
        "total": total_count,
        "submitted": submitted_count,
        "draft": draft_count,
        "total_amount": float(total_amount_value) if total_amount_value else 0
    }
