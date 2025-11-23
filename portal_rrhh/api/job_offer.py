import frappe
from frappe import _

@frappe.whitelist()
def get_job_offers_by_employee(employee_name):
    """Get job offers for a specific employee"""
    try:
        # Primero obtener el DNI/NIE del empleado
        Employee = frappe.qb.DocType("Employee")
        employee_query = (
            frappe.qb.from_(Employee)
            .select(Employee.custom_dninie)
            .where(Employee.name == employee_name)
        )

        employee_data = employee_query.run(as_dict=True)
        if not employee_data:
            return []

        employee_dni = employee_data[0].get('custom_dninie')
        if not employee_dni:
            return []

        JobOffer = frappe.qb.DocType("Job Offer")

        query = (
            frappe.qb.from_(JobOffer)
            .select(
                JobOffer.name,
                JobOffer.job_applicant,
                JobOffer.applicant_name,
                JobOffer.applicant_email,
                JobOffer.status,
                JobOffer.offer_date,
                JobOffer.designation,
                JobOffer.company,
                JobOffer.creation,
                JobOffer.modified,
                JobOffer.custom_fecha_inicio,
                JobOffer.custom_fecha_fin,
                JobOffer.custom_tipo_de_contrato,
                JobOffer.custom_estado_de_tramitacion,
                JobOffer.custom_firmado,
                JobOffer.custom_contrato,
                JobOffer.custom_comun,
                JobOffer.workflow_state,
                JobOffer.curso,
                JobOffer.expediente,
                JobOffer.centro_formacion,
                JobOffer.custom_provincia
            )
            .where(JobOffer.custom_dninie == employee_dni)
            .orderby(JobOffer.creation, order=frappe.qb.desc)
            .limit(20)  # Limitar resultados para mejor rendimiento
        )

        job_offers = query.run(as_dict=True)
        return job_offers
    except Exception as e:
        frappe.log_error(f"Error en get_job_offers_by_employee: {str(e)}", "Job Offer API Error")
        return []

@frappe.whitelist()
def get_job_offer(name):
    """Get specific job offer details"""
    JobOffer = frappe.qb.DocType("Job Offer")

    query = (
        frappe.qb.from_(JobOffer)
        .select("*")
        .where(JobOffer.name == name)
        .limit(1)
    )

    job_offer = query.run(as_dict=True)
    if not len(job_offer):
        frappe.throw(_("Job Offer not found"), frappe.DoesNotExistError)

    return job_offer[0]

@frappe.whitelist()
def get_contratacion_stats():
    """Get statistics for contratacion dashboard"""
    JobOffer = frappe.qb.DocType("Job Offer")

    # Get all job offers
    query = frappe.qb.from_(JobOffer).select("*")
    job_offers = query.run(as_dict=True)

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
