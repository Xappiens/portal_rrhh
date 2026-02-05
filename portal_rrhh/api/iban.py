import frappe
from frappe import _
from frappe.utils import nowdate


@frappe.whitelist()
def get_my_iban_requests():
    """Obtener todas las solicitudes de cambio de IBAN del empleado actual"""
    # Obtener el empleado del usuario actual
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return []

    # Obtener todas las solicitudes del empleado
    requests = frappe.get_all(
        "IBAN Change Request",
        filters={"employee": employee},
        fields=[
            "name",
            "status",
            "current_iban",
            "new_iban",
            "bank_entity",
            "posting_date",
            "approval_notes",
            "reason",
            "certificate_attachment",
            "modified",
            "creation"
        ],
        order_by="creation desc"
    )

    return requests


@frappe.whitelist()
def create_iban_change_request(**kwargs):
    """
    Create a new IBAN Change Request
    Puede recibir los datos como parámetros individuales o como dict 'data'
    """
    import json
    
    # Obtener datos de kwargs o de form_dict
    if 'data' in kwargs:
        data = kwargs['data']
    elif kwargs:
        # Si se pasan parámetros individuales, usarlos directamente
        data = kwargs
    else:
        # Intentar obtener de form_dict
        data = frappe.form_dict.get('data') or frappe.form_dict
    
    # Si es string, parsearlo
    if isinstance(data, str):
        data = json.loads(data)
    
    # Si aún no hay data, lanzar error
    if not data:
        frappe.throw(_("No se proporcionaron datos para crear la solicitud."))

    # Verificar que el usuario tiene un empleado asociado
    current_user_employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not current_user_employee:
        frappe.throw(_("No se encontró un empleado asociado a tu usuario."))

    # Verificar que el empleado de la solicitud coincide con el usuario actual
    employee_id = data.get("employee")
    if employee_id != current_user_employee:
        frappe.throw(_("Solo puedes crear solicitudes de cambio de IBAN para tu propio perfil de empleado."))

    # Verificar que el empleado existe
    if not frappe.db.exists("Employee", employee_id):
        frappe.throw(_("El empleado especificado no existe."))

    # Crear el documento
    doc = frappe.new_doc("IBAN Change Request")
    doc.employee = employee_id
    doc.new_iban = data.get("new_iban", "").replace(" ", "").upper()
    doc.reason = data.get("reason", "")
    doc.certificate_attachment = data.get("certificate_attachment")
    doc.posting_date = nowdate()

    # El documento se validará automáticamente al insertar
    # Las validaciones incluyen:
    # - Formato IBAN español
    # - Dígito de control IBAN
    # - Vinculación usuario-empleado
    # - Cálculo de entidad bancaria
    # - Establecimiento de IBAN actual
    # - Creación de notificaciones (si is_new() es True)

    try:
        # Log para depuración antes de insertar
        frappe.logger().info(f"Intentando crear IBAN Change Request para empleado {employee_id}, IBAN: {doc.new_iban}, Certificado: {bool(doc.certificate_attachment)}")
        
        # Insertar el documento
        # Las validaciones se ejecutarán automáticamente en validate()
        # incluyendo create_notification() si is_new() es True
        doc.insert(ignore_permissions=True)
        
        # Forzar commit para asegurar que las notificaciones se guarden
        frappe.db.commit()
        
        # Log para depuración después de insertar
        frappe.logger().info(f"IBAN Change Request creado exitosamente: {doc.name} para empleado {employee_id}")
        
        return doc.name
    except frappe.ValidationError as ve:
        # Re-lanzar errores de validación sin modificar
        error_msg = str(ve)
        frappe.log_error(f"Validation error creating IBAN Change Request: {error_msg}", "IBAN Change Request Validation Error")
        frappe.throw(_(error_msg))
    except Exception as e:
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        frappe.log_error(f"Error creating IBAN Change Request: {error_msg}\n{error_trace}", "IBAN Change Request Error")
        frappe.throw(_(f"Error al crear la solicitud: {error_msg}"))
