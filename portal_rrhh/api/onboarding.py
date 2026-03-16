import frappe
from frappe import _
from frappe.utils import today, getdate, add_days


def create_onboarding_process_if_needed(doc, method=None):
    """
    Creates an Employee Onboarding Process when Job Offer status changes to 'Alta'.
    
    Este hook se ejecuta en on_update, on_submit y on_update_after_submit.
    
    Lógica:
    1. Solo procesar si el workflow_state actual es 'Alta'
    2. Detectar si es un CAMBIO a Alta (no una actualización de un doc que ya estaba en Alta)
    3. Validar que la fecha_fin no esté en el pasado
    4. Verificar que no exista ya un proceso de onboarding para este Job Offer
    5. Buscar el empleado vinculado
    6. Crear el proceso con los documentos correspondientes a la empresa
    """
    
    # 1. Solo procesar si el estado actual es 'Alta'
    if doc.workflow_state != "Alta":
        return
    
    # 2. Detectar si es un CAMBIO a Alta usando _doc_before_save
    # Frappe guarda automáticamente el estado anterior del documento
    doc_before_save = doc.get_doc_before_save()
    
    if doc_before_save:
        previous_workflow_state = doc_before_save.workflow_state
        
        # Si el estado anterior ya era 'Alta', es solo una actualización menor
        if previous_workflow_state == "Alta":
            return
    else:
        # Si no hay doc_before_save, es un documento nuevo
        # En on_submit de un documento nuevo, sí debemos procesar
        # Pero verificamos que no hayamos procesado ya este Job Offer
        pass
    
    # 3. Validar que custom_fecha_fin no esté en el pasado
    if doc.custom_fecha_fin:
        fecha_fin = getdate(doc.custom_fecha_fin)
        hoy = getdate(today())
        
        if fecha_fin < hoy:
            frappe.log_error(
                f"Onboarding NO creado para Job Offer {doc.name}: fecha_fin ({doc.custom_fecha_fin}) ya pasó",
                "Onboarding - Fecha Fin Pasada"
            )
            return
    
    # 4. Verificar si ya existe un proceso de onboarding para este Job Offer
    # Solo bloquear si existe uno Pending, In Progress o Completed
    existing_process = frappe.db.exists("Employee Onboarding Process", {
        "job_offer": doc.name,
        "onboarding_status": ["in", ["Pending", "In Progress", "Completed"]]
    })
    
    if existing_process:
        return
    
    # 5. Buscar el empleado vinculado al Job Offer
    employee_name = _find_employee_for_job_offer(doc)
    
    if not employee_name:
        # No se encontró empleado - esto puede pasar si el Job Offer se pasa a Alta
        # antes de crear el Employee. Registrar para debug pero no es error.
        frappe.log_error(
            f"Onboarding NO creado para Job Offer {doc.name}: no se encontró empleado vinculado. "
            f"job_applicant={doc.job_applicant}, custom_dninie={doc.get('custom_dninie')}, "
            f"custom_empleado={doc.get('custom_empleado')}",
            "Onboarding - Empleado No Encontrado"
        )
        return
    
    # 6. Obtener documentos de onboarding para la empresa del Job Offer
    valid_docs = _get_onboarding_documents_for_company(doc.company)
    
    if not valid_docs:
        frappe.log_error(
            f"Onboarding NO creado para Job Offer {doc.name}: "
            f"no hay documentos de onboarding configurados para la empresa {doc.company}",
            "Onboarding - Sin Documentos"
        )
        return
    
    # 7. Crear el proceso de onboarding
    # Preservar el usuario que hizo el cambio en el Job Offer como owner del proceso
    current_user = frappe.session.user
    
    try:
        process = frappe.new_doc("Employee Onboarding Process")
        process.employee = employee_name
        process.job_offer = doc.name
        process.company = doc.company
        process.start_date = today()
        process.onboarding_status = "Pending"
        
        # Asignar el owner como el usuario que cambió el Job Offer a Alta
        process.owner = current_user
        
        for d in valid_docs:
            row = process.append("required_documents", {})
            row.document_reference = d.name
            row.document_title = d.title
            row.document_type = d.document_type
            row.is_required = 1
            row.is_completed = 0
        
        process.flags.ignore_permissions = True
        process.insert()
        frappe.db.commit()
        
        frappe.log_error(
            f"✅ Onboarding CREADO: {process.name} para empleado {employee_name}, "
            f"Job Offer {doc.name}, {len(valid_docs)} documentos, creado por {current_user}",
            "Onboarding - Creado Exitosamente"
        )
        
    except Exception as e:
        frappe.log_error(
            f"Error creando onboarding para Job Offer {doc.name}: {str(e)}\n{frappe.get_traceback()}",
            "Onboarding - Error de Creación"
        )


def _find_employee_for_job_offer(doc):
    """
    Busca el empleado vinculado a un Job Offer.
    
    Orden de búsqueda:
    1. Por custom_dninie (campo personalizado con el DNI/NIE)
    2. Por custom_empleado (campo personalizado con link directo)
    3. Por job_applicant (campo estándar)
    4. Por applicant_email -> user_id del Employee
    5. Por applicant_email -> personal_email del Employee
    """
    employee_name = None
    
    # 1. Buscar por custom_dninie (el DNI/NIE es el ID del empleado)
    if doc.get("custom_dninie"):
        if frappe.db.exists("Employee", doc.custom_dninie):
            employee_name = doc.custom_dninie
    
    # 2. Buscar por custom_empleado
    if not employee_name and doc.get("custom_empleado"):
        if frappe.db.exists("Employee", doc.custom_empleado):
            employee_name = doc.custom_empleado
    
    # 3. Buscar por job_applicant
    if not employee_name and doc.job_applicant:
        employee_name = frappe.db.get_value(
            "Employee", 
            {"job_applicant": doc.job_applicant}, 
            "name"
        )
    
    # 4. Buscar por applicant_email -> user_id
    if not employee_name and doc.applicant_email:
        employee_name = frappe.db.get_value(
            "Employee", 
            {"user_id": doc.applicant_email}, 
            "name"
        )
    
    # 5. Buscar por applicant_email -> personal_email
    if not employee_name and doc.applicant_email:
        employee_name = frappe.db.get_value(
            "Employee", 
            {"personal_email": doc.applicant_email}, 
            "name"
        )
    
    return employee_name


def _get_onboarding_documents_for_company(company):
    """
    Obtiene los documentos de onboarding configurados para una empresa específica.
    
    Un documento aplica si:
    - checkbox_onboarding = 1
    - workflow_state = 'Vigente'
    - La empresa está en la lista de System Document Company del documento
    """
    docs = frappe.get_all(
        "Documentos del sistema",
        filters={
            "checkbox_onboarding": 1,
            "workflow_state": "Vigente"
        },
        fields=["name", "title", "document_type"]
    )
    
    valid_docs = []
    for d in docs:
        allowed_companies = frappe.get_all(
            "System Document Company",
            filters={"parent": d.name},
            pluck="company"
        )
        
        # Solo incluir si la empresa del Job Offer está en la lista
        if allowed_companies and company in allowed_companies:
            valid_docs.append(d)
    
    return valid_docs


@frappe.whitelist()
def get_my_onboarding_docs():
    """
    Returns the list of documents for the logged-in employee's onboarding history (ALL processes).
    """
    user = frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    
    if not employee:
        return []

    # FETCH ALL PROCESSES (Pending, Completed, Cancelled - everything)
    # Sorted by newest first so the UI shows latest first
    # FILTER: Exclude Cancelled processes (docstatus=2 or onboarding_status="Cancelled")
    processes = frappe.get_all("Employee Onboarding Process",
                               filters={
                                   "employee": employee,
                                   "onboarding_status": ["!=", "Cancelled"],
                                   "docstatus": ["!=", 2]
                               },
                               fields=["name", "onboarding_status", "creation", "target_completion_date"],
                               order_by="creation desc")

    if not processes:
        return []
    
    all_docs_list = []

    for proc_info in processes:
        process = frappe.get_doc("Employee Onboarding Process", proc_info.name)
        
        # Process Title (Constructed for UI context)
        # e.g. "Onboarding 2025 (Completed)"
        creation_date = frappe.utils.format_date(process.creation)
        process_title = f"{process.name} - {creation_date}"

        for row in process.required_documents:
            doc_details = frappe.get_value("Documentos del sistema", row.document_reference, 
                                           ["descripcion", "fichero", "documento_adjunto", "title", "document_type"], as_dict=True)
            
            if not doc_details:
                 continue

            all_docs_list.append({
                "process_name": process.name,
                "process_status": process.onboarding_status, # UI might want to badge this
                "process_creation": process.creation,
                "process_title": process_title, # Helper for grouping
                "row_name": row.name, 
                "document_reference": row.document_reference,
                "title": doc_details.title,
                "type": doc_details.document_type,
                "description": doc_details.descripcion,
                "is_completed": row.is_completed,
                "completion_date": row.completion_date,
                "file_url": doc_details.documento_adjunto,
                "html_content": doc_details.fichero
            })

    return all_docs_list



@frappe.whitelist()
def has_pending_onboarding():
    """
    Checks if the logged-in employee has any pending onboarding process.
    Returns: { "has_pending": bool }
    """
    user = frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    
    if not employee:
        return {"has_pending": False}

    # Check for any process that is NOT Cancelled and NOT Completed
    # Statuses: Pending, In Progress
    pending_count = frappe.db.count("Employee Onboarding Process", {
        "employee": employee,
        "docstatus": ["<", 2], # Draft or Submitted (though Submitted usually implies validated/completed, but let's stick to status)
        "onboarding_status": ["in", ["Pending", "In Progress"]]
    })
    
    return {"has_pending": pending_count > 0}

@frappe.whitelist()
def ping():
    return "pong"
