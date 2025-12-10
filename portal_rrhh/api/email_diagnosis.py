"""
API para diagnóstico de problemas de correo
"""
import frappe
from frappe import _
from portal_rrhh.utils.email_handler import get_email_diagnosis_info


@frappe.whitelist()
def get_email_diagnosis():
    """
    Obtiene información de diagnóstico sobre problemas de correo con @burgosatu.es
    """
    frappe.only_for("System Manager")
    
    try:
        info = get_email_diagnosis_info()
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        frappe.log_error(f"Error al obtener diagnóstico de correo: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

