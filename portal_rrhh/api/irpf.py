import frappe
from frappe import _
from frappe.utils import nowdate


@frappe.whitelist()
def get_my_irpf_requests():
    """Obtener todas las solicitudes de retención IRPF del empleado actual"""
    # Obtener el empleado del usuario actual
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return []

    # Obtener todas las solicitudes del empleado
    requests = frappe.get_all(
        "IRPF Retention Request",
        filters={"employee": employee},
        fields=[
            "name",
            "status",
            "current_irpf",
            "requested_irpf",
            "irpf_type",
            "effective_date",
            "posting_date",
            "approval_notes",
            "reason",
            "approved_by",
            "approval_date",
            "modified",
            "creation"
        ],
        order_by="creation desc"
    )

    return requests


@frappe.whitelist()
def get_current_irpf():
    """Obtener el IRPF actual del empleado"""
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return {"current_irpf": 0}
    
    emp_doc = frappe.get_doc("Employee", employee)
    current_irpf = emp_doc.get("custom_irpf", "")
    
    if current_irpf:
        try:
            current_irpf = float(current_irpf.replace(",", ".").replace("%", "").strip())
        except (ValueError, AttributeError):
            current_irpf = 0
    else:
        current_irpf = 0
    
    return {"current_irpf": current_irpf}


@frappe.whitelist()
def create_irpf_retention_request(**kwargs):
    """
    Create a new IRPF Retention Request
    Puede recibir los datos como parámetros individuales o como dict 'data'
    """
    import json
    
    # Obtener datos de kwargs o de form_dict
    if 'data' in kwargs:
        data = kwargs['data']
    elif kwargs:
        data = kwargs
    else:
        data = frappe.form_dict.get('data') or frappe.form_dict
    
    # Si es string, parsearlo
    if isinstance(data, str):
        data = json.loads(data)
    
    if not data:
        frappe.throw(_("No se proporcionaron datos para crear la solicitud."))

    # Verificar que el usuario tiene un empleado asociado
    current_user_employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not current_user_employee:
        frappe.throw(_("No se encontró un empleado asociado a tu usuario."))

    # Verificar que el empleado de la solicitud coincide con el usuario actual
    employee_id = data.get("employee")
    if employee_id != current_user_employee:
        frappe.throw(_("Solo puedes crear solicitudes de retención IRPF para tu propio perfil de empleado."))

    # Verificar que el empleado existe
    if not frappe.db.exists("Employee", employee_id):
        frappe.throw(_("El empleado especificado no existe."))

    # Crear el documento
    doc = frappe.new_doc("IRPF Retention Request")
    doc.employee = employee_id
    doc.requested_irpf = float(data.get("requested_irpf", 0))
    doc.irpf_type = data.get("irpf_type", "Incremento voluntario")
    doc.effective_date = data.get("effective_date")
    doc.reason = data.get("reason", "")
    doc.voluntary_declaration = data.get("voluntary_declaration", 0)
    doc.posting_date = nowdate()

    try:
        frappe.logger().info(f"Intentando crear IRPF Retention Request para empleado {employee_id}, IRPF: {doc.requested_irpf}%")
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        frappe.logger().info(f"IRPF Retention Request creado exitosamente: {doc.name} para empleado {employee_id}")
        
        return doc.name
    except frappe.ValidationError as ve:
        error_msg = str(ve)
        frappe.log_error(f"Validation error creating IRPF Retention Request: {error_msg}", "IRPF Retention Request Validation Error")
        frappe.throw(_(error_msg))
    except Exception as e:
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        frappe.log_error(f"Error creating IRPF Retention Request: {error_msg}\n{error_trace}", "IRPF Retention Request Error")
        frappe.throw(_(f"Error al crear la solicitud: {error_msg}"))
