import frappe
from frappe import _

@frappe.whitelist()
def get_modificaciones_by_employee(employee_name):
    """Get modificaciones RRHH for a specific employee"""
    frappe.log_error(f"🔍 Modificaciones API - employee_name recibido: {employee_name}", "Modificaciones API Debug")

    # Primero obtener el DNI/NIE del empleado
    Employee = frappe.qb.DocType("Employee")
    employee_query = (
        frappe.qb.from_(Employee)
        .select(Employee.custom_dninie)
        .where(Employee.name == employee_name)
    )

    employee_data = employee_query.run(as_dict=True)
    if not employee_data:
        frappe.log_error(f"🔍 Modificaciones API - No se encontró empleado: {employee_name}", "Modificaciones API Debug")
        return []

    employee_dni = employee_data[0].get('custom_dninie')
    if not employee_dni:
        frappe.log_error(f"🔍 Modificaciones API - Empleado sin DNI/NIE: {employee_name}", "Modificaciones API Debug")
        return []

    frappe.log_error(f"🔍 Modificaciones API - DNI del empleado: {employee_dni}", "Modificaciones API Debug")

    ModificacionesRRHH = frappe.qb.DocType("Modificaciones RRHH")

    query = (
        frappe.qb.from_(ModificacionesRRHH)
        .select(
            ModificacionesRRHH.name,
            ModificacionesRRHH.company,
            ModificacionesRRHH.employee,
            ModificacionesRRHH.designation,
            ModificacionesRRHH.start_date,
            ModificacionesRRHH.end_date,
            ModificacionesRRHH.status,
            ModificacionesRRHH.job_offer,
            ModificacionesRRHH.tipo_actualizacion,
            ModificacionesRRHH.custom_estado_de_tramitacion,
            ModificacionesRRHH.custom_tipo_de_contrato,
            ModificacionesRRHH.custom_provincia,
            ModificacionesRRHH.custom_firmado,
            ModificacionesRRHH.custom_comun,
            ModificacionesRRHH.workflow_state,
            ModificacionesRRHH.creation,
            ModificacionesRRHH.modified
        )
        .where(ModificacionesRRHH.employee == employee_name)
        .orderby(ModificacionesRRHH.creation, order=frappe.qb.desc)
    )

    modificaciones = query.run(as_dict=True)
    frappe.log_error(f"🔍 Modificaciones API - Modificaciones encontradas: {len(modificaciones)}", "Modificaciones API Debug")
    return modificaciones

@frappe.whitelist()
def get_modificaciones_by_job_offer(job_offer_name):
    """Get modificaciones RRHH for a specific job offer"""
    try:
        ModificacionesRRHH = frappe.qb.DocType("Modificaciones RRHH")

        query = (
            frappe.qb.from_(ModificacionesRRHH)
            .select(
                ModificacionesRRHH.name,
                ModificacionesRRHH.company,
                ModificacionesRRHH.employee,
                ModificacionesRRHH.designation,
                ModificacionesRRHH.start_date,
                ModificacionesRRHH.end_date,
                ModificacionesRRHH.status,
                ModificacionesRRHH.job_offer,
                ModificacionesRRHH.tipo_actualizacion,
                ModificacionesRRHH.custom_estado_de_tramitacion,
                ModificacionesRRHH.custom_tipo_de_contrato,
                ModificacionesRRHH.custom_provincia,
                ModificacionesRRHH.custom_firmado,
                ModificacionesRRHH.custom_comun,
                ModificacionesRRHH.workflow_state,
                ModificacionesRRHH.creation,
                ModificacionesRRHH.modified
            )
            .where(ModificacionesRRHH.job_offer == job_offer_name)
            .orderby(ModificacionesRRHH.creation, order=frappe.qb.desc)
            .limit(50)  # Limitar resultados para mejor rendimiento
        )

        modificaciones = query.run(as_dict=True)
        return modificaciones
    except Exception as e:
        frappe.log_error(f"Error en get_modificaciones_by_job_offer: {str(e)}", "Modificaciones API Error")
        return []
