import frappe
from frappe import _
from frappe.utils import today, getdate, formatdate, flt
from datetime import datetime


@frappe.whitelist()
def get_appraisals(filters=None, limit=20, offset=0, order_by="creation desc"):
    """Obtener lista de evaluaciones con filtros avanzados"""
    CompetencyAppraisal = frappe.qb.DocType("Competency Appraisal")
    Employee = frappe.qb.DocType("Employee")
    AppraisalCycle = frappe.qb.DocType("Appraisal Cycle")
    CompetencyProfile = frappe.qb.DocType("Competency Profile")
    
    # Parse filters
    if filters and isinstance(filters, str):
        import json
        filters = json.loads(filters)
    
    query = (
        frappe.qb.from_(CompetencyAppraisal)
        .left_join(Employee).on(CompetencyAppraisal.employee == Employee.name)
        .left_join(AppraisalCycle).on(CompetencyAppraisal.appraisal_cycle == AppraisalCycle.name)
        .left_join(CompetencyProfile).on(CompetencyAppraisal.competency_profile == CompetencyProfile.name)
        .select(
            CompetencyAppraisal.name,
            CompetencyAppraisal.employee,
            CompetencyAppraisal.employee_name,
            CompetencyAppraisal.appraisal_cycle,
            CompetencyAppraisal.competency_profile,
            CompetencyAppraisal.status,
            CompetencyAppraisal.evaluation_date,
            CompetencyAppraisal.total_score,
            CompetencyAppraisal.self_appraisal_score,
            CompetencyAppraisal.self_appraisal_enabled,
            CompetencyAppraisal.evaluated_by,
            CompetencyAppraisal.creation,
            CompetencyAppraisal.modified,
            Employee.department,
            Employee.designation,
            Employee.company,
            Employee.image,
            AppraisalCycle.cycle_name,
            AppraisalCycle.start_date,
            AppraisalCycle.end_date,
            CompetencyProfile.profile_name
        )
    )
    
    # Apply filters
    if filters:
        if filters.get('status'):
            if isinstance(filters['status'], list):
                query = query.where(CompetencyAppraisal.status.isin(filters['status']))
            else:
                query = query.where(CompetencyAppraisal.status == filters['status'])
        
        if filters.get('employee'):
            query = query.where(CompetencyAppraisal.employee == filters['employee'])
        
        if filters.get('appraisal_cycle'):
            query = query.where(CompetencyAppraisal.appraisal_cycle == filters['appraisal_cycle'])
        
        if filters.get('department'):
            query = query.where(Employee.department == filters['department'])
        
        if filters.get('company'):
            query = query.where(Employee.company == filters['company'])
        
        if filters.get('designation'):
            query = query.where(Employee.designation == filters['designation'])
        
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            query = query.where(
                (CompetencyAppraisal.employee_name.like(search_term)) |
                (CompetencyAppraisal.name.like(search_term)) |
                (Employee.name.like(search_term))
            )
        
        if filters.get('date_from'):
            query = query.where(CompetencyAppraisal.evaluation_date >= filters['date_from'])
        
        if filters.get('date_to'):
            query = query.where(CompetencyAppraisal.evaluation_date <= filters['date_to'])
    
    # Order by
    if order_by:
        order_field, order_direction = order_by.split() if ' ' in order_by else (order_by, 'desc')
        if order_field == 'creation':
            if order_direction.lower() == 'desc':
                query = query.orderby(CompetencyAppraisal.creation, order=frappe.qb.desc)
            else:
                query = query.orderby(CompetencyAppraisal.creation, order=frappe.qb.asc)
        elif order_field == 'employee_name':
            if order_direction.lower() == 'desc':
                query = query.orderby(CompetencyAppraisal.employee_name, order=frappe.qb.desc)
            else:
                query = query.orderby(CompetencyAppraisal.employee_name, order=frappe.qb.asc)
        elif order_field == 'total_score':
            if order_direction.lower() == 'desc':
                query = query.orderby(CompetencyAppraisal.total_score, order=frappe.qb.desc)
            else:
                query = query.orderby(CompetencyAppraisal.total_score, order=frappe.qb.asc)
    
    # Apply pagination
    appraisals = query.limit(limit).offset(offset).run(as_dict=True)
    
    # Filtrar por permisos - solo incluir evaluaciones que el usuario puede leer
    filtered_appraisals = []
    for appraisal in appraisals:
        try:
            # Verificar permisos de lectura para cada evaluación
            if frappe.has_permission("Competency Appraisal", "read", appraisal.get('name')):
                filtered_appraisals.append(appraisal)
        except:
            # Si hay error verificando permisos, omitir el documento
            continue
    
    appraisals = filtered_appraisals
    
    # Enrich with additional data
    for appraisal in appraisals:
        # Get competency evaluations count
        appraisal['competency_count'] = frappe.db.count(
            "Competency Evaluation",
            {"parent": appraisal.name}
        )
        
        # Format dates
        if appraisal.get('evaluation_date'):
            appraisal['evaluation_date_formatted'] = formatdate(appraisal['evaluation_date'])
        if appraisal.get('creation'):
            appraisal['creation_formatted'] = formatdate(appraisal['creation'])
    
    # Nota: El total_count no refleja el filtrado por permisos porque se calcula antes
    # Para obtener un conteo preciso, sería necesario obtener todos los registros y filtrarlos
    # Por ahora, usamos el conteo de los resultados filtrados como aproximación
    return {
        'appraisals': appraisals,
        'total_count': len(appraisals)  # Usar el conteo de resultados filtrados
    }


@frappe.whitelist()
def get_appraisal_details(name):
    """Obtener detalles completos de una evaluación"""
    # Usar frappe.get_doc que respeta permisos automáticamente
    appraisal = frappe.get_doc("Competency Appraisal", name)
    # Verificar permisos de lectura
    if not frappe.has_permission("Competency Appraisal", "read", appraisal):
        frappe.throw(_("No tienes permisos para ver esta evaluación"), frappe.PermissionError)
    
    # Get competency evaluations with full details
    competency_evaluations = []
    for eval_item in appraisal.competency_evaluations:
        competency = frappe.get_doc("Competency", eval_item.competency)
        
        # Get competency levels
        levels = []
        for level in competency.competency_levels:
            levels.append({
                'level_number': level.level_number,
                'level_name': level.level_name,
                'description': level.description
            })
        
        competency_evaluations.append({
            'competency': eval_item.competency,
            'competency_name': competency.competency_name,
            'competency_code': competency.competency_code,
            'category': competency.category,
            'description': competency.description,
            'expected_level': eval_item.expected_level,
            'achieved_level': eval_item.achieved_level,
            'level_gap': eval_item.level_gap,
            'weightage': eval_item.weightage,
            'score': eval_item.score,
            'comments': eval_item.comments,
            'employee_comments': eval_item.employee_comments,
            'evidence': eval_item.evidence,
            'levels': levels,
            'max_level': max([l.level_number for l in competency.competency_levels]) if competency.competency_levels else 0
        })
    
    # Get employee info
    employee = frappe.get_doc("Employee", appraisal.employee)
    
    # Get appraisal cycle info
    cycle = None
    if appraisal.appraisal_cycle:
        cycle = frappe.get_doc("Appraisal Cycle", appraisal.appraisal_cycle)
    
    # Get competency profile info
    profile = None
    if appraisal.competency_profile:
        profile = frappe.get_doc("Competency Profile", appraisal.competency_profile)
    
    # Get previous appraisal if exists
    previous_appraisal = None
    if appraisal.previous_appraisal:
        try:
            previous_appraisal = frappe.get_doc("Competency Appraisal", appraisal.previous_appraisal)
        except frappe.DoesNotExistError:
            pass
    
    # Get evaluator info
    evaluator = None
    if appraisal.evaluated_by:
        try:
            evaluator = frappe.get_doc("User", appraisal.evaluated_by)
        except frappe.DoesNotExistError:
            pass
    
    # Calculate statistics
    stats = {
        'total_competencies': len(competency_evaluations),
        'competencies_evaluated': len([e for e in competency_evaluations if e['achieved_level'] is not None]),
        'competencies_with_gap': len([e for e in competency_evaluations if e.get('level_gap', 0) > 0]),
        'competencies_critical_gap': len([e for e in competency_evaluations if e.get('level_gap', 0) >= 2]),
        'average_gap': sum([e.get('level_gap', 0) for e in competency_evaluations]) / len(competency_evaluations) if competency_evaluations else 0,
        'total_weightage': sum([e.get('weightage', 0) for e in competency_evaluations])
    }
    
    return {
        'appraisal': appraisal.as_dict(),
        'competency_evaluations': competency_evaluations,
        'employee': {
            'name': employee.name,
            'employee_name': employee.employee_name,
            'department': employee.department,
            'designation': employee.designation,
            'company': employee.company,
            'image': employee.image,
            'date_of_joining': employee.date_of_joining
        },
        'cycle': cycle.as_dict() if cycle else None,
        'profile': profile.as_dict() if profile else None,
        'previous_appraisal': previous_appraisal.as_dict() if previous_appraisal else None,
        'evaluator': {
            'name': evaluator.name,
            'full_name': evaluator.full_name
        } if evaluator else None,
        'statistics': stats
    }


@frappe.whitelist()
def create_appraisal(data):
    """Crear nueva evaluación"""
    import json
    if isinstance(data, str):
        data = json.loads(data)
    
    appraisal = frappe.get_doc({
        'doctype': 'Competency Appraisal',
        'employee': data.get('employee'),
        'appraisal_cycle': data.get('appraisal_cycle'),
        'competency_profile': data.get('competency_profile'),
        'status': 'Borrador',
        'self_appraisal_enabled': data.get('self_appraisal_enabled', 0)
    })
    
    appraisal.insert()
    
    return {
        'name': appraisal.name,
        'message': _('Evaluación creada exitosamente')
    }


@frappe.whitelist()
def update_appraisal(name, data):
    """Actualizar evaluación"""
    import json
    if isinstance(data, str):
        data = json.loads(data)
    
    appraisal = frappe.get_doc("Competency Appraisal", name)
    
    # Update basic fields
    updatable_fields = [
        'appraisal_cycle', 'competency_profile', 'status', 
        'self_appraisal_enabled', 'self_appraisal_date',
        'interview_date', 'interview_notes', 'improvement_suggestions'
    ]
    
    for field in updatable_fields:
        if field in data:
            setattr(appraisal, field, data[field])
    
    # Update competency evaluations if provided
    if 'competency_evaluations' in data:
        appraisal.set('competency_evaluations', [])
        for eval_data in data['competency_evaluations']:
            appraisal.append('competency_evaluations', {
                'competency': eval_data.get('competency'),
                'expected_level': eval_data.get('expected_level'),
                'achieved_level': eval_data.get('achieved_level'),
                'weightage': eval_data.get('weightage'),
                'comments': eval_data.get('comments'),
                'employee_comments': eval_data.get('employee_comments'),
                'evidence': eval_data.get('evidence')
            })
    
    appraisal.save()
    
    return {
        'name': appraisal.name,
        'message': _('Evaluación actualizada exitosamente')
    }


@frappe.whitelist()
def submit_appraisal(name):
    """Enviar/completar evaluación"""
    appraisal = frappe.get_doc("Competency Appraisal", name)
    
    if appraisal.status == "Completado":
        frappe.throw(_("Esta evaluación ya está completada"))
    
    appraisal.status = "Enviado"
    appraisal.save()
    
    try:
        appraisal.submit()
    except Exception as e:
        frappe.throw(str(e))
    
    return {
        'name': appraisal.name,
        'status': appraisal.status,
        'message': _('Evaluación enviada exitosamente')
    }


@frappe.whitelist()
def cancel_appraisal(name):
    """Cancelar evaluación"""
    appraisal = frappe.get_doc("Competency Appraisal", name)
    appraisal.status = "Cancelado"
    appraisal.save()
    
    return {
        'name': appraisal.name,
        'message': _('Evaluación cancelada exitosamente')
    }


@frappe.whitelist()
def get_appraisal_statistics(filters=None):
    """Obtener estadísticas de evaluaciones"""
    if filters and isinstance(filters, str):
        import json
        filters = json.loads(filters)
    
    # Base filters
    base_filters = {}
    if filters:
        if filters.get('appraisal_cycle'):
            base_filters['appraisal_cycle'] = filters['appraisal_cycle']
        if filters.get('company'):
            base_filters['company'] = filters['company']
    
    # Total evaluaciones
    total_appraisals = frappe.db.count("Competency Appraisal", base_filters)
    
    # Por estado
    status_counts = {}
    for status in ["Borrador", "Auto-evaluado", "Enviado", "Completado", "Cancelado"]:
        status_filters = {**base_filters, 'status': status}
        status_counts[status] = frappe.db.count("Competency Appraisal", status_filters)
    
    # Promedio de puntuación (solo completadas)
    avg_score_result = frappe.db.sql("""
        SELECT AVG(total_score) as avg_score, COUNT(*) as count
        FROM `tabCompetency Appraisal`
        WHERE status = 'Completado'
        AND total_score IS NOT NULL
    """, as_dict=True)
    
    avg_score = avg_score_result[0].avg_score if avg_score_result and avg_score_result[0].avg_score else 0
    completed_count = avg_score_result[0].count if avg_score_result else 0
    
    # Evaluaciones pendientes
    pending_filters = {**base_filters, 'status': ['in', ['Borrador', 'Auto-evaluado']]}
    pending_count = frappe.db.count("Competency Appraisal", pending_filters)
    
    # Evaluaciones por mes (últimos 6 meses)
    monthly_data = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(creation, '%%Y-%%m') as month,
            COUNT(*) as count
        FROM `tabCompetency Appraisal`
        WHERE creation >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        GROUP BY DATE_FORMAT(creation, '%%Y-%%m')
        ORDER BY month DESC
    """, as_dict=True)
    
    # Evaluaciones con brechas críticas
    critical_gaps = frappe.db.sql("""
        SELECT COUNT(DISTINCT parent) as count
        FROM `tabCompetency Evaluation`
        WHERE level_gap >= 2
        AND parent IN (
            SELECT name FROM `tabCompetency Appraisal` 
            WHERE status = 'Completado'
        )
    """, as_dict=True)
    
    critical_gaps_count = critical_gaps[0].count if critical_gaps else 0
    
    return {
        'total_appraisals': total_appraisals,
        'status_counts': status_counts,
        'average_score': flt(avg_score, 2),
        'completed_count': completed_count,
        'pending_count': pending_count,
        'critical_gaps_count': critical_gaps_count,
        'monthly_data': monthly_data
    }


@frappe.whitelist()
def get_appraisal_cycles(filters=None):
    """Obtener ciclos de evaluación"""
    if filters and isinstance(filters, str):
        import json
        filters = json.loads(filters)
    
    cycle_filters = {}
    if filters:
        if filters.get('status'):
            if isinstance(filters['status'], list):
                cycle_filters['status'] = ['in', filters['status']]
            else:
                cycle_filters['status'] = filters['status']
        if filters.get('company'):
            cycle_filters['company'] = filters['company']
    
    cycles = frappe.get_all(
        "Appraisal Cycle",
        filters=cycle_filters,
        fields=['name', 'cycle_name', 'start_date', 'end_date', 'status', 'company'],
        order_by='start_date desc'
    )
    
    # Enrich with appraisal counts
    for cycle in cycles:
        cycle['appraisal_count'] = frappe.db.count(
            "Competency Appraisal",
            {"appraisal_cycle": cycle.name}
        )
        cycle['completed_count'] = frappe.db.count(
            "Competency Appraisal",
            {"appraisal_cycle": cycle.name, "status": "Completado"}
        )
    
    return cycles


@frappe.whitelist()
def get_competency_profiles(filters=None):
    """Obtener perfiles de competencias"""
    if filters and isinstance(filters, str):
        import json
        filters = json.loads(filters)
    
    profile_filters = {}
    if filters:
        if filters.get('designation'):
            profile_filters['designation'] = filters['designation']
        if filters.get('company'):
            profile_filters['company'] = filters['company']
    
    profiles = frappe.get_all(
        "Competency Profile",
        filters=profile_filters,
        fields=['name', 'profile_name', 'designation', 'company', 'is_default'],
        order_by='profile_name'
    )
    
    # Enrich with competency counts
    for profile in profiles:
        profile['competency_count'] = frappe.db.count(
            "Competency Profile Item",
            {"parent": profile.name}
        )
    
    return profiles


@frappe.whitelist()
def get_competencies(filters=None):
    """Obtener todas las competencias"""
    if filters and isinstance(filters, str):
        import json
        filters = json.loads(filters)
    
    competency_filters = {}
    if filters:
        if filters.get('category'):
            competency_filters['category'] = filters['category']
    
    competencies = frappe.get_all(
        "Competency",
        filters=competency_filters,
        fields=['name', 'competency_name', 'competency_code', 'category'],
        order_by='competency_name'
    )
    
    return competencies


@frappe.whitelist()
def get_gap_analysis(filters=None):
    """Obtener análisis de brechas de competencias"""
    if filters and isinstance(filters, str):
        import json
        filters = json.loads(filters)
    
    # Base query
    base_filters = {}
    if filters:
        if filters.get('appraisal_cycle'):
            base_filters['appraisal_cycle'] = filters['appraisal_cycle']
        if filters.get('company'):
            base_filters['company'] = filters['company']
    
    # Get evaluations with gaps
    gap_analysis = frappe.db.sql("""
        SELECT 
            ce.competency,
            c.competency_name,
            c.competency_code,
            c.category,
            COUNT(*) as evaluation_count,
            AVG(ce.level_gap) as avg_gap,
            MAX(ce.level_gap) as max_gap,
            COUNT(CASE WHEN ce.level_gap >= 2 THEN 1 END) as critical_count
        FROM `tabCompetency Evaluation` ce
        INNER JOIN `tabCompetency Appraisal` ca ON ce.parent = ca.name
        INNER JOIN `tabCompetency` c ON ce.competency = c.name
        WHERE ce.level_gap > 0
        AND ca.status = 'Completado'
        GROUP BY ce.competency, c.competency_name, c.competency_code, c.category
        HAVING avg_gap > 0
        ORDER BY avg_gap DESC
        LIMIT 20
    """, as_dict=True)
    
    return gap_analysis


@frappe.whitelist()
def bulk_create_appraisals(data):
    """Crear múltiples evaluaciones desde un ciclo"""
    import json
    if isinstance(data, str):
        data = json.loads(data)
    
    cycle_name = data.get('appraisal_cycle')
    if not cycle_name:
        frappe.throw(_("Debe especificar un ciclo de evaluación"))
    
    cycle = frappe.get_doc("Appraisal Cycle", cycle_name)
    employees = data.get('employees', [])
    
    created = []
    errors = []
    
    for employee_name in employees:
        try:
            employee = frappe.get_doc("Employee", employee_name)
            
            # Get competency profile for employee designation
            profile = frappe.db.get_value(
                "Competency Profile",
                {"designation": employee.designation, "company": employee.company},
                "name"
            )
            
            if not profile:
                errors.append({
                    'employee': employee_name,
                    'error': _("No se encontró perfil de competencias para {0}").format(employee.designation)
                })
                continue
            
            # Check if appraisal already exists
            existing = frappe.db.exists(
                "Competency Appraisal",
                {
                    "employee": employee_name,
                    "appraisal_cycle": cycle_name,
                    "status": ["!=", "Cancelado"]
                }
            )
            
            if existing:
                errors.append({
                    'employee': employee_name,
                    'error': _("Ya existe una evaluación para este empleado en este ciclo")
                })
                continue
            
            appraisal = frappe.get_doc({
                'doctype': 'Competency Appraisal',
                'employee': employee_name,
                'appraisal_cycle': cycle_name,
                'competency_profile': profile,
                'status': 'Borrador'
            })
            
            appraisal.insert()
            created.append(appraisal.name)
            
        except Exception as e:
            errors.append({
                'employee': employee_name,
                'error': str(e)
            })
    
    return {
        'created': created,
        'errors': errors,
        'message': _('Se crearon {0} evaluaciones exitosamente').format(len(created))
    }


@frappe.whitelist()
def get_departments():
    """Obtener lista de departamentos"""
    departments = frappe.get_all(
        "Department",
        fields=['name', 'department_name'],
        order_by='department_name'
    )
    return departments


@frappe.whitelist()
def get_designations():
    """Obtener lista de designaciones"""
    designations = frappe.get_all(
        "Designation",
        fields=['name', 'description'],
        order_by='description'
    )
    return designations

