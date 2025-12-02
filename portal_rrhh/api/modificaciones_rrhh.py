import frappe
from frappe import _

@frappe.whitelist()
def get_modificaciones_by_employee(employee_name):
    """Get modificaciones RRHH for a specific employee"""
    try:
        # Verificar primero que el usuario tenga permisos para ver el empleado
        try:
            employee = frappe.get_doc("Employee", employee_name)
            if not frappe.has_permission("Employee", "read", employee):
                frappe.throw(_("No tienes permisos para ver este empleado"), frappe.PermissionError)
        except frappe.DoesNotExistError:
            return []

        # Usar frappe.get_list para respetar permisos automáticamente
        modificaciones = frappe.get_list(
            "Modificaciones RRHH",
            fields=[
                "name",
                "company",
                "employee",
                "designation",
                "start_date",
                "end_date",
                "status",
                "job_offer",
                "tipo_actualizacion",
                "custom_estado_de_tramitacion",
                "custom_tipo_de_contrato",
                "custom_provincia",
                "custom_firmado",
                "custom_comun",
                "workflow_state",
                "creation",
                "modified"
            ],
            filters={"employee": employee_name},
            order_by="creation desc"
        )
        
        return modificaciones
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error en get_modificaciones_by_employee: {str(e)}", "Modificaciones API Error")
        return []

@frappe.whitelist()
def get_modificaciones_by_job_offer(job_offer_name):
    """Get modificaciones RRHH for a specific job offer"""
    try:
        # Verificar primero que el usuario tenga permisos para ver la Job Offer
        try:
            job_offer = frappe.get_doc("Job Offer", job_offer_name)
            if not frappe.has_permission("Job Offer", "read", job_offer):
                frappe.throw(_("No tienes permisos para ver esta Job Offer"), frappe.PermissionError)
        except frappe.DoesNotExistError:
            return []

        # Usar frappe.get_list para respetar permisos automáticamente
        modificaciones = frappe.get_list(
            "Modificaciones RRHH",
            fields=[
                "name",
                "company",
                "employee",
                "designation",
                "start_date",
                "end_date",
                "status",
                "job_offer",
                "tipo_actualizacion",
                "custom_estado_de_tramitacion",
                "custom_tipo_de_contrato",
                "custom_provincia",
                "custom_firmado",
                "custom_comun",
                "workflow_state",
                "creation",
                "modified"
            ],
            filters={"job_offer": job_offer_name},
            order_by="creation desc",
            limit_page_length=50
        )
        
        return modificaciones
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error en get_modificaciones_by_job_offer: {str(e)}", "Modificaciones API Error")
        return []
