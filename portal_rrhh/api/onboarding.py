import frappe
from frappe import _
from frappe.utils import today, getdate, add_days

# Force reload check - 2026-02-02
def create_onboarding_process_if_needed(doc, method=None):
    """
    Creates an Employee Onboarding Process when Job Offer status is 'Alta'.
    
    Validaciones implementadas:
    - Problema 2: Si custom_fecha_fin está en el pasado, no crear onboarding
    - Problema 3: Solo crear onboarding cuando el workflow_state CAMBIA a Alta (no en cualquier update)
    - Problema 4: Si ya existe un onboarding COMPLETADO para esta Job Offer, no crear otro
    """
    if doc.workflow_state != "Alta":
        return

    # ========================================================================
    # PROBLEMA 3: Solo crear onboarding cuando el workflow_state CAMBIA a Alta
    # No en cualquier update de una Job Offer que ya estaba en Alta
    # ========================================================================
    
    # Obtener el valor anterior del workflow_state desde la base de datos
    previous_workflow_state = frappe.db.get_value("Job Offer", doc.name, "workflow_state")
    
    # Si el documento ya existía y el workflow_state anterior también era "Alta",
    # significa que es solo una actualización menor, no un cambio de estado
    if previous_workflow_state == "Alta":
        # Es una actualización de una Job Offer que ya estaba en Alta
        # No crear nuevo onboarding
        return

    # ========================================================================
    # PROBLEMA 2: Validar que custom_fecha_fin no esté en el pasado
    # Si la fecha fin ya pasó, la contratación ya terminó y no necesita onboarding
    # ========================================================================
    
    if doc.custom_fecha_fin:
        fecha_fin = getdate(doc.custom_fecha_fin)
        hoy = getdate(today())
        
        if fecha_fin < hoy:
            # La contratación ya finalizó, no crear onboarding
            frappe.log_error(
                f"Onboarding NO creado para Job Offer {doc.name}: fecha_fin ({doc.custom_fecha_fin}) ya pasó",
                "Onboarding Validation - Fecha Fin Pasada"
            )
            return

    # ========================================================================
    # PROBLEMA 4: Verificar si ya existe un onboarding completado o en curso
    # Estados que bloquean: Pending, In Progress, Completed
    # Solo se permite crear si el anterior fue Cancelled
    # ========================================================================
    
    # Verificar si existe un proceso en estado Pending, In Progress o Completed
    existing_process = frappe.db.exists("Employee Onboarding Process", {
        "job_offer": doc.name,
        "onboarding_status": ["in", ["Pending", "In Progress", "Completed"]]
    })

    if existing_process:
        # Ya existe un proceso pendiente, en curso o completado, no crear otro
        return

    # Find relevant Employee
    # 1. Check if Job Offer serves as link (custom field not seen, so verify standard)
    # 2. Check Employee where job_applicant matches
    employee_name = None
    if doc.job_applicant:
        employee_name = frappe.db.get_value("Employee", {"job_applicant": doc.job_applicant}, "name")
    
    # Fallback: Check if there is an employee with the applicant_email
    if not employee_name and doc.applicant_email:
        # Check by user_id or personal_email or company_email
        employee_name = frappe.db.get_value("Employee", {"user_id": doc.applicant_email}, "name")
        if not employee_name:
             employee_name = frappe.db.get_value("Employee", {"personal_email": doc.applicant_email}, "name")
    
    if not employee_name:
        # If no employee found, we cannot create the process yet.
        # This might happen if Job Offer is set to Alta BEFORE Employee creation.
        # Ideally, this should also be hooked to Employee creation to check for Alta Job Offers.
        return

    # Create the Process
    process = frappe.new_doc("Employee Onboarding Process")
    process.employee = employee_name
    process.job_offer = doc.name
    process.company = doc.company
    process.start_date = today()
    process.onboarding_status = "Pending"
    
    # Find System Documents marked for Onboarding
    # Filter: checkbox_onboarding = 1 AND workflow_state = 'Vigente'
    docs = frappe.get_all("Documentos del sistema",
                          filters={
                              "checkbox_onboarding": 1, 
                              "workflow_state": "Vigente"
                          },
                          fields=["name", "title", "document_type"])

    valid_docs = []
    for d in docs:
        # Check specific companies
        allowed_companies = frappe.get_all("System Document Company", filters={"parent": d.name}, pluck="company")
        
        # If no specific companies defined, it applies to NONE (as per user request).
        # If companies defined, Job Offer's company must be in the list.
        if allowed_companies and doc.company in allowed_companies:
            valid_docs.append(d)

    if not valid_docs:
        return

    for d in valid_docs:
        row = process.append("required_documents", {})
        row.document_reference = d.name
        row.document_title = d.title
        row.document_type = d.document_type
        row.is_required = 1
        row.is_completed = 0
    
    if not process.required_documents:
        frappe.log_error(f"Onboarding Aborted: {doc.name}", "Attempted to create process with no documents.")
        return

    process.insert(ignore_permissions=True)
    frappe.db.commit()


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
