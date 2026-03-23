from contextlib import contextmanager

import frappe
from frappe import _
from frappe.model.docstatus import DocStatus
from frappe.utils import cint, cstr, getdate, formatdate


def _user_can_manage_employee_incentives():
	"""Portal users often lack Employee read; gate búsqueda de empleados en incentivos."""
	if frappe.has_permission("Employee Incentive", "create") or frappe.has_permission(
		"Employee Incentive", "write"
	):
		return True
	# Rol dedicado sin fila explícita en DocPerm (solo lectura + flujo)
	if "Supervisión de Incentivos" in frappe.get_roles() and frappe.has_permission(
		"Employee Incentive", "read"
	):
		return True
	return False


def _current_user_employee_name():
	return frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")


def _user_can_read_incentives_portal():
	if _user_can_manage_employee_incentives():
		return True
	return frappe.has_permission("Employee Incentive", "read")


def _can_view_incentive_doc(doc):
	"""Creador del doc o responsable (reports_to) del empleado del incentivo."""
	if doc.owner == frappe.session.user:
		return True
	me = _current_user_employee_name()
	if not me:
		return False
	rep = frappe.db.get_value("Employee", doc.employee, "reports_to")
	return rep == me


def _portal_user_is_creator_or_designated_approver(owner, designated_approver_employee):
	"""Quien creó el incentivo o el empleado indicado en Incentivo Aprobado Por."""
	user = frappe.session.user
	if owner == user:
		return True
	me = _current_user_employee_name()
	return bool(me and designated_approver_employee and me == designated_approver_employee)


@contextmanager
def _bypass_document_workflow_validation():
	"""El workflow de Employee Incentive filtra por rol; el portal valida creador/aprobador designado."""
	import frappe.model.document as document_module

	original = document_module.validate_workflow

	def _noop_validate_workflow(_doc):
		return

	document_module.validate_workflow = _noop_validate_workflow
	try:
		yield
	finally:
		document_module.validate_workflow = original


def _portal_apply_employee_incentive_transition(doc, action: str):
	"""Replica la lógica de ``apply_workflow`` sin comprobar roles del workflow."""
	from frappe.model.workflow import WorkflowTransitionError, get_workflow, is_transition_condition_satisfied

	workflow = get_workflow(doc.doctype)
	ws_field = workflow.workflow_state_field
	current_state = (doc.get(ws_field) or "").strip() or "Borrador"

	transition_row = None
	for t in workflow.transitions:
		if t.state == current_state and cstr(t.action).strip() == cstr(action).strip():
			transition_row = t
			break

	if not transition_row:
		frappe.throw(_("Acción no disponible en el estado actual del incentivo."), WorkflowTransitionError)

	if transition_row.condition and not is_transition_condition_satisfied(transition_row, doc):
		frappe.throw(_("No se cumplen las condiciones para esta acción."), frappe.ValidationError)

	doc.set(ws_field, transition_row.next_state)

	next_states = [s for s in workflow.states if s.state == transition_row.next_state]
	if not next_states:
		frappe.throw(_("Estado de workflow desconocido: {0}").format(transition_row.next_state))
	next_state_row = next_states[0]

	if next_state_row.update_field:
		doc.set(next_state_row.update_field, next_state_row.update_value)

	new_docstatus = cint(next_state_row.doc_status)
	doc.flags.ignore_permissions = True

	with _bypass_document_workflow_validation():
		if doc.docstatus.is_draft() and new_docstatus == DocStatus.draft():
			doc.save()
		elif doc.docstatus.is_draft() and new_docstatus == DocStatus.submitted():
			doc.submit()
		elif doc.docstatus.is_submitted() and new_docstatus == DocStatus.submitted():
			doc.save()
		elif doc.docstatus.is_submitted() and new_docstatus == DocStatus.cancelled():
			doc.cancel()
		else:
			frappe.throw(
				_("Transición de estado no soportada (docstatus {0} → {1}).").format(
					doc.docstatus, new_docstatus
				)
			)

	try:
		doc.add_comment("Workflow", _("Portal RRHH: {0}").format(action))
	except Exception:
		pass


@frappe.whitelist()
def portal_approve_employee_incentive(name):
	"""Validar incentivo (transición ``Validar``: Borrador → Validado). Solo creador o aprobador designado."""
	doc = frappe.get_doc("Employee Incentive", cstr(name))
	if not _can_view_incentive_doc(doc):
		frappe.throw(_("No tienes permiso para este incentivo"), frappe.PermissionError)
	if not _portal_user_is_creator_or_designated_approver(doc.owner, doc.custom_incentivo_aprobado_por):
		frappe.throw(_("Solo el creador o el responsable designado pueden validar"), frappe.PermissionError)

	ws = (doc.workflow_state or "").strip() or "Borrador"
	if ws != "Borrador" or doc.docstatus != 0:
		frappe.throw(_("Solo se puede validar un incentivo en borrador (Borrador)."))

	_portal_apply_employee_incentive_transition(doc, "Validar")
	doc.reload()
	return {"success": True, "workflow_state": doc.workflow_state, "docstatus": doc.docstatus}


@frappe.whitelist()
def portal_cancel_employee_incentive(name):
	"""Cancelar: elimina borradores (Borrador/Validado docstatus 0) o transición Cancelar si está enviado (Solicitado)."""
	name = cstr(name)
	doc = frappe.get_doc("Employee Incentive", name)
	if not _can_view_incentive_doc(doc):
		frappe.throw(_("No tienes permiso para este incentivo"), frappe.PermissionError)
	if not _portal_user_is_creator_or_designated_approver(doc.owner, doc.custom_incentivo_aprobado_por):
		frappe.throw(_("Solo el creador o el responsable designado pueden cancelar"), frappe.PermissionError)

	ws = (doc.workflow_state or "").strip() or "Borrador"
	ds = cint(doc.docstatus)

	if ds == 0 and ws in ("Borrador", "Validado"):
		doc.flags.ignore_permissions = True
		doc.delete()
		return {"success": True, "deleted": True}

	if ds == 1 and ws == "Solicitado":
		_portal_apply_employee_incentive_transition(doc, "Cancelar")
		doc.reload()
		return {"success": True, "deleted": False, "workflow_state": doc.workflow_state, "docstatus": doc.docstatus}

	frappe.throw(_("No se puede cancelar este incentivo en su estado actual."))


@frappe.whitelist()
def list_employee_incentives_for_portal(
	desde=None, hasta=None, estado=None, employee_search=None, limit=100
):
	"""Lista incentivos visibles en portal: creados por el usuario o del equipo (soy ``reports_to``)."""
	if not _user_can_read_incentives_portal():
		frappe.throw(_("No tienes permiso para ver incentivos"), frappe.PermissionError)

	user = frappe.session.user
	me_emp = _current_user_employee_name()
	lim = min(max(cint(limit) or 100, 1), 200)

	if me_emp:
		visibility = "(ei.owner = %(user)s OR IFNULL(e.reports_to, '') = %(me_emp)s)"
		params = {"user": user, "me_emp": me_emp, "limit": lim}
	else:
		visibility = "ei.owner = %(user)s"
		params = {"user": user, "limit": lim}

	conditions = [visibility]

	if desde:
		conditions.append("ei.payroll_date >= %(desde)s")
		params["desde"] = getdate(desde)
	if hasta:
		conditions.append("ei.payroll_date <= %(hasta)s")
		params["hasta"] = getdate(hasta)

	estado = cstr(estado or "").strip()
	if estado == "Draft":
		conditions.append("ei.docstatus = 0")
	elif estado == "Approved":
		conditions.append("ei.docstatus = 1")
	elif estado == "Rejected":
		conditions.append("IFNULL(ei.workflow_state, '') = 'Rejected'")

	es = cstr(employee_search or "").strip()
	if es:
		conditions.append("ei.employee_name LIKE %(emp)s")
		params["emp"] = f"%{es}%"

	where_sql = " AND ".join(conditions)

	rows = frappe.db.sql(
		f"""
		SELECT
			ei.name,
			ei.owner,
			ei.employee,
			ei.employee_name,
			ei.department,
			ei.company,
			ei.salary_component,
			ei.incentive_amount,
			ei.payroll_date,
			ei.custom_provincia,
			ei.custom_by_hours,
			ei.custom_incentive_hours,
			ei.custom_justificación,
			ei.custom_incentivo_aprobado_por,
			ei.docstatus,
			ei.workflow_state,
			ap.employee_name AS custom_incentivo_aprobado_por_name
		FROM `tabEmployee Incentive` ei
		INNER JOIN `tabEmployee` e ON e.name = ei.employee
		LEFT JOIN `tabEmployee` ap ON ap.name = ei.custom_incentivo_aprobado_por
		WHERE {where_sql}
		ORDER BY ei.payroll_date DESC, ei.modified DESC
		LIMIT %(limit)s
		""",
		params,
		as_dict=True,
	)

	for row in rows:
		can_act = _portal_user_is_creator_or_designated_approver(
			row.get("owner"), row.get("custom_incentivo_aprobado_por")
		)
		ws = (row.get("workflow_state") or "").strip() or "Borrador"
		ds = cint(row.get("docstatus"))
		row["portal_can_approve"] = bool(can_act and ws == "Borrador" and ds == 0)
		cancel_del = bool(can_act and ds == 0 and ws in ("Borrador", "Validado"))
		cancel_wf = bool(can_act and ds == 1 and ws == "Solicitado")
		row["portal_can_cancel"] = cancel_del or cancel_wf
		row["portal_cancel_deletes_record"] = bool(cancel_del)

	return rows


@frappe.whitelist()
def save_employee_incentive_portal(**kwargs):
	"""Crear o actualizar incentivo desde portal, incl. ``custom_incentivo_aprobado_por`` (campo read-only en Desk)."""
	name = cstr(kwargs.get("name") or "").strip() or None

	if name:
		doc = frappe.get_doc("Employee Incentive", name)
		if not _can_view_incentive_doc(doc):
			frappe.throw(_("No tienes permiso para editar este incentivo"), frappe.PermissionError)
		if doc.docstatus != 0:
			frappe.throw(_("Solo se pueden editar borradores"), frappe.ValidationError)

		if not kwargs.get("salary_component"):
			frappe.throw(_("Componente salarial obligatorio"))

		doc.salary_component = kwargs.get("salary_component")
		doc.payroll_date = kwargs.get("payroll_date")
		doc.incentive_amount = frappe.utils.flt(kwargs.get("incentive_amount"))
		doc.custom_provincia = cstr(kwargs.get("custom_provincia") or "").strip() or None
		doc.custom_by_hours = cint(kwargs.get("custom_by_hours"))
		doc.custom_incentive_hours = cstr(kwargs.get("custom_incentive_hours") or "").strip() or None
		doc.custom_justificación = cstr(kwargs.get("custom_justificación") or "").strip() or None
		aprob = cstr(kwargs.get("custom_incentivo_aprobado_por") or "").strip()
		if not aprob:
			frappe.throw(_("Indica el responsable que validará el incentivo"))
		doc.custom_incentivo_aprobado_por = aprob

		doc.save(ignore_permissions=True)
		return {"name": doc.name, "success": True}

	frappe.has_permission("Employee Incentive", "create", throw=True)

	employee = cstr(kwargs.get("employee") or "").strip()
	if not employee:
		frappe.throw(_("Empleado obligatorio"))
	if not kwargs.get("salary_component"):
		frappe.throw(_("Componente salarial obligatorio"))

	aprob = cstr(kwargs.get("custom_incentivo_aprobado_por") or "").strip()
	if not aprob:
		frappe.throw(_("Indica el responsable que validará el incentivo"))

	doc = frappe.new_doc("Employee Incentive")
	doc.employee = employee
	doc.salary_component = kwargs.get("salary_component")
	doc.payroll_date = kwargs.get("payroll_date")
	doc.incentive_amount = frappe.utils.flt(kwargs.get("incentive_amount"))
	doc.custom_provincia = cstr(kwargs.get("custom_provincia") or "").strip() or None
	doc.custom_by_hours = cint(kwargs.get("custom_by_hours"))
	doc.custom_incentive_hours = cstr(kwargs.get("custom_incentive_hours") or "").strip() or None
	doc.custom_justificación = cstr(kwargs.get("custom_justificación") or "").strip() or None
	doc.custom_incentivo_aprobado_por = aprob

	doc.insert(ignore_permissions=True)
	return {"name": doc.name, "success": True}


@frappe.whitelist()
def search_employees_for_incentive(search_text=None, limit=50):
	"""Buscar empleados activos para el modal de incentivos (todas las categorías).

	Excluye el registro de empleado vinculado al usuario de la sesión (``Employee.user_id``),
	para no incentivar el propio usuario.

	Requiere los mismos permisos que el resto del flujo de incentivos en portal.
	"""
	if not _user_can_manage_employee_incentives():
		frappe.throw(_("No tienes permiso para buscar empleados en incentivos"), frappe.PermissionError)

	search = cstr(search_text or "").strip()
	lim = cint(limit) or 50
	lim = min(max(lim, 1), 100)

	if len(search) < 2:
		return []

	pattern = f"%{search}%"
	params = {"p": pattern, "lim": lim}
	exclude_employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	exclude_sql = ""
	if exclude_employee:
		exclude_sql = " AND e.name != %(exclude_employee)s"
		params["exclude_employee"] = exclude_employee

	rows = frappe.db.sql(
		f"""
		SELECT
			e.name,
			e.employee_name,
			e.department,
			e.designation,
			e.reports_to,
			rt.employee_name AS reports_to_name
		FROM `tabEmployee` e
		LEFT JOIN `tabEmployee` rt ON rt.name = e.reports_to
		WHERE e.status = 'Active'
			AND (
				e.employee_name LIKE %(p)s
				OR e.name LIKE %(p)s
				OR IFNULL(e.custom_dninie, '') LIKE %(p)s
			)
			{exclude_sql}
		ORDER BY e.employee_name ASC
		LIMIT %(lim)s
		""",
		params,
		as_dict=True,
	)

	return rows


@frappe.whitelist()
def search_employees_for_approver(search_text=None, limit=50):
	"""Buscar empleados activos para el campo responsable/aprobador (sin excluir al usuario)."""
	if not _user_can_read_incentives_portal():
		frappe.throw(_("No tienes permiso para buscar responsables"), frappe.PermissionError)

	search = cstr(search_text or "").strip()
	lim = cint(limit) or 50
	lim = min(max(lim, 1), 100)

	if len(search) < 2:
		return []

	pattern = f"%{search}%"
	params = {"p": pattern, "lim": lim}

	return frappe.db.sql(
		"""
		SELECT e.name, e.employee_name, e.department, e.designation
		FROM `tabEmployee` e
		WHERE e.status = 'Active'
			AND (
				e.employee_name LIKE %(p)s
				OR e.name LIKE %(p)s
				OR IFNULL(e.custom_dninie, '') LIKE %(p)s
			)
		ORDER BY e.employee_name ASC
		LIMIT %(lim)s
		""",
		params,
		as_dict=True,
	)


@frappe.whitelist()
def search_docente_employees_for_incentive(search_text=None, limit=50):
	"""Compatibilidad: mismo comportamiento que ``search_employees_for_incentive``."""
	return search_employees_for_incentive(search_text, limit)


@frappe.whitelist()
def get_job_offer_provincias_for_incentive(search_text=None, limit=300):
	"""Provincias distintas usadas en Job Offer (``custom_provincia``), para el campo provincia del incentivo.

	Filtro opcional por texto (LIKE). Misma autorización que la búsqueda de empleados en incentivos.
	"""
	if not _user_can_manage_employee_incentives():
		frappe.throw(_("No tienes permiso para listar provincias de incentivos"), frappe.PermissionError)

	lim = min(max(cint(limit) or 300, 1), 500)
	search = cstr(search_text or "").strip()
	params = {"lim": lim}
	if search:
		where_clause = "IFNULL(custom_provincia,'') != '' AND custom_provincia LIKE %(st)s"
		params["st"] = f"%{search}%"
	else:
		where_clause = "IFNULL(custom_provincia,'') != ''"

	rows = frappe.db.sql(
		f"""
		SELECT DISTINCT custom_provincia AS name
		FROM `tabJob Offer`
		WHERE {where_clause}
		ORDER BY custom_provincia
		LIMIT %(lim)s
		""",
		params,
		as_list=True,
	)
	return [r[0] for r in rows if r[0]]


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
