import frappe
from frappe import _

@frappe.whitelist()
def get_job_offers_by_employee(employee_name):
    """Get job offers for a specific employee"""
    try:
        # Verificar primero que el usuario tenga permisos para ver el empleado
        try:
            employee = frappe.get_doc("Employee", employee_name)
            if not frappe.has_permission("Employee", "read", employee):
                frappe.throw(_("No tienes permisos para ver este empleado"), frappe.PermissionError)
        except frappe.DoesNotExistError:
            return []
        
        employee_dni = employee.get('custom_dninie')
        if not employee_dni:
            return []

        # Usar frappe.get_list para respetar permisos automáticamente
        job_offers = frappe.get_list(
            "Job Offer",
            fields=[
                "name",
                "job_applicant",
                "applicant_name",
                "applicant_email",
                "status",
                "offer_date",
                "designation",
                "company",
                "creation",
                "modified",
                "custom_fecha_inicio",
                "custom_fecha_fin",
                "custom_tipo_de_contrato",
                "custom_estado_de_tramitacion",
                "custom_firmado",
                "custom_contrato",
                "custom_comun",
                "workflow_state",
                "curso",
                "expediente",
                "centro_formacion",
                "custom_provincia"
            ],
            filters={"custom_dninie": employee_dni},
            order_by="creation desc",
            limit_page_length=20
        )
        
        return job_offers
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error en get_job_offers_by_employee: {str(e)}", "Job Offer API Error")
        return []

@frappe.whitelist()
def get_job_offer(name):
    """Get specific job offer details"""
    # Usar frappe.get_doc que respeta permisos automáticamente
    try:
        job_offer = frappe.get_doc("Job Offer", name)
        # Verificar permisos de lectura
        if not frappe.has_permission("Job Offer", "read", job_offer):
            frappe.throw(_("No tienes permisos para ver esta Job Offer"), frappe.PermissionError)
        return job_offer.as_dict()
    except frappe.DoesNotExistError:
        frappe.throw(_("Job Offer not found"), frappe.DoesNotExistError)

@frappe.whitelist()
def get_contratacion_stats():
    """Get statistics for contratacion dashboard"""
    # Usar frappe.get_list para respetar permisos automáticamente
    job_offers = frappe.get_list(
        "Job Offer",
        fields=["name", "status", "custom_fecha_inicio", "custom_fecha_fin"]
    )

    # Calculate current week dates
    from frappe.utils import getdate, get_first_day, get_last_day
    from datetime import datetime, timedelta

    now = getdate()
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Calculate stats
    bajas_esta_semana = 0
    altas_esta_semana = 0
    contratos_pendientes = 0
    contratos_firmados = 0

    for offer in job_offers:
        # Bajas esta semana: Job Offer en estado "Alta" con custom_fecha_fin esta semana
        if (offer.get('custom_fecha_fin') and
            offer.get('status') == 'Alta' and
            getdate(offer.get('custom_fecha_fin')) >= start_of_week and
            getdate(offer.get('custom_fecha_fin')) <= end_of_week):
            bajas_esta_semana += 1

        # Altas esta semana: Job Offer en estado "Alta" con custom_fecha_inicio esta semana
        if (offer.get('custom_fecha_inicio') and
            offer.get('status') == 'Alta' and
            getdate(offer.get('custom_fecha_inicio')) >= start_of_week and
            getdate(offer.get('custom_fecha_inicio')) <= end_of_week):
            altas_esta_semana += 1

        # Anexos que terminan (Pendientes)
        if offer.get('status') == 'Pending':
            contratos_pendientes += 1

        # Nuevos anexos (Aceptados)
        if offer.get('status') == 'Accepted':
            contratos_firmados += 1

    return {
        'bajas_esta_semana': bajas_esta_semana,
        'altas_esta_semana': altas_esta_semana,
        'contratos_pendientes': contratos_pendientes,
        'contratos_firmados': contratos_firmados
    }
