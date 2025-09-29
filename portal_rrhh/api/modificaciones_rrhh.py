import frappe
from frappe import _

@frappe.whitelist()
def get_modificaciones_by_employee(employee_name):
    """Get modificaciones RRHH for a specific employee"""
    Modificaciones = frappe.qb.DocType("Modificaciones RRHH")

    query = (
        frappe.qb.from_(Modificaciones)
        .select(
            Modificaciones.name,
            Modificaciones.company,
            Modificaciones.employee,
            Modificaciones.designation,
            Modificaciones.start_date,
            Modificaciones.end_date,
            Modificaciones.status,
            Modificaciones.tipo_actualizacion,
            Modificaciones.job_offer,
            Modificaciones.creation,
            Modificaciones.modified,
            Modificaciones.custom_estado_de_tramitacion,
            Modificaciones.custom_tipo_de_contrato,
            Modificaciones.custom_provincia,
            Modificaciones.custom_firmado,
            Modificaciones.custom_comun,
            Modificaciones.workflow_state,
            Modificaciones.curso,
            Modificaciones.expediente,
            Modificaciones.centro_formacion
        )
        .where(Modificaciones.employee == employee_name)
        .orderby(Modificaciones.creation, order=frappe.qb.desc)
    )

    modificaciones = query.run(as_dict=True)
    return modificaciones

@frappe.whitelist()
def get_modificacion(name):
    """Get specific modificacion details"""
    Modificaciones = frappe.qb.DocType("Modificaciones RRHH")

    query = (
        frappe.qb.from_(Modificaciones)
        .select("*")
        .where(Modificaciones.name == name)
        .limit(1)
    )

    modificacion = query.run(as_dict=True)
    if not len(modificacion):
        frappe.throw(_("Modificacion RRHH not found"), frappe.DoesNotExistError)

    return modificacion[0]
