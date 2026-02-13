import frappe
from frappe import _
from frappe.utils import nowdate
import json


@frappe.whitelist()
def get_my_modelo_145_list():
    """Obtener todos los Modelo 145 del empleado actual"""
    # Obtener el empleado del usuario actual
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return []

    # Obtener todos los modelos del empleado
    modelos = frappe.get_all(
        "Modelo 145",
        filters={"employee": employee},
        fields=[
            "name",
            "status",
            "posting_date",
            "effective_date",
            "family_situation",
            "disability_grade",
            "received_date",
            "received_by",
            "modified",
            "creation"
        ],
        order_by="creation desc"
    )

    # Añadir conteo de descendientes y ascendientes
    for modelo in modelos:
        modelo["descendants_count"] = frappe.db.count(
            "Modelo 145 Descendiente", 
            filters={"parent": modelo["name"]}
        )
        modelo["ascendants_count"] = frappe.db.count(
            "Modelo 145 Ascendiente", 
            filters={"parent": modelo["name"]}
        )

    return modelos


@frappe.whitelist()
def get_latest_modelo_145():
    """Obtener el Modelo 145 más reciente del empleado"""
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return None

    modelo = frappe.get_all(
        "Modelo 145",
        filters={"employee": employee},
        fields=["*"],
        order_by="creation desc",
        limit=1
    )

    if not modelo:
        return None

    modelo = modelo[0]
    
    # Obtener descendientes
    modelo["descendants"] = frappe.get_all(
        "Modelo 145 Descendiente",
        filters={"parent": modelo["name"]},
        fields=["year_of_birth", "year_of_adoption", "disability_grade", "disability_needs_help"]
    )
    
    # Obtener ascendientes
    modelo["ascendants"] = frappe.get_all(
        "Modelo 145 Ascendiente",
        filters={"parent": modelo["name"]},
        fields=["year_of_birth", "cohabiting_descendants", "disability_grade", "disability_needs_help"]
    )

    return modelo


@frappe.whitelist()
def has_modelo_145():
    """Verificar si el empleado tiene al menos un Modelo 145 presentado"""
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return {"has_modelo": False, "count": 0}

    count = frappe.db.count("Modelo 145", filters={"employee": employee})
    return {"has_modelo": count > 0, "count": count}


@frappe.whitelist()
def create_modelo_145(**kwargs):
    """
    Crear un nuevo Modelo 145
    Puede recibir los datos como parámetros individuales o como dict 'data'
    """
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
        frappe.throw(_("No se proporcionaron datos para crear el Modelo 145."))

    # Verificar que el usuario tiene un empleado asociado
    current_user_employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not current_user_employee:
        frappe.throw(_("No se encontró un empleado asociado a tu usuario."))

    # Verificar que el empleado de la solicitud coincide con el usuario actual
    employee_id = data.get("employee")
    if employee_id != current_user_employee:
        frappe.throw(_("Solo puedes presentar el Modelo 145 para tu propio perfil de empleado."))

    # Verificar que el empleado existe
    if not frappe.db.exists("Employee", employee_id):
        frappe.throw(_("El empleado especificado no existe."))

    # Crear el documento
    doc = frappe.new_doc("Modelo 145")
    doc.employee = employee_id
    doc.effective_date = data.get("effective_date")
    doc.posting_date = nowdate()
    doc.signature_date = nowdate()
    
    # Situación familiar
    doc.family_situation = data.get("family_situation", "3. Otra situación")
    doc.spouse_nif = data.get("spouse_nif", "")
    
    # Discapacidad del perceptor
    doc.disability_grade = data.get("disability_grade", "")
    doc.disability_needs_help = data.get("disability_needs_help", 0)
    
    # Movilidad geográfica
    doc.geographic_mobility = data.get("geographic_mobility", 0)
    doc.mobility_date = data.get("mobility_date")
    
    # Custodia exclusiva
    doc.descendants_exclusive_custody = data.get("descendants_exclusive_custody", 0)
    
    # Pensiones
    doc.alimony_spouse = data.get("alimony_spouse", 0)
    doc.alimony_children = data.get("alimony_children", 0)
    
    # Vivienda y rendimientos irregulares
    doc.housing_deduction = data.get("housing_deduction", 0)
    doc.irregular_income_previous = data.get("irregular_income_previous", 0)
    
    # Declaración responsable
    doc.declaration_accepted = data.get("declaration_accepted", 0)
    
    # Añadir descendientes
    descendants = data.get("descendants", [])
    if isinstance(descendants, str):
        descendants = json.loads(descendants)
    
    for desc in descendants:
        doc.append("descendants", {
            "year_of_birth": desc.get("year_of_birth"),
            "year_of_adoption": desc.get("year_of_adoption"),
            "disability_grade": desc.get("disability_grade", ""),
            "disability_needs_help": desc.get("disability_needs_help", 0)
        })
    
    # Añadir ascendientes
    ascendants = data.get("ascendants", [])
    if isinstance(ascendants, str):
        ascendants = json.loads(ascendants)
    
    for asc in ascendants:
        doc.append("ascendants", {
            "year_of_birth": asc.get("year_of_birth"),
            "cohabiting_descendants": asc.get("cohabiting_descendants"),
            "disability_grade": asc.get("disability_grade", ""),
            "disability_needs_help": asc.get("disability_needs_help", 0)
        })

    try:
        frappe.logger().info(f"Intentando crear Modelo 145 para empleado {employee_id}")
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        frappe.logger().info(f"Modelo 145 creado exitosamente: {doc.name} para empleado {employee_id}")
        
        return doc.name
    except frappe.ValidationError as ve:
        error_msg = str(ve)
        frappe.log_error(f"Validation error creating Modelo 145: {error_msg}", "Modelo 145 Validation Error")
        frappe.throw(_(error_msg))
    except Exception as e:
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        frappe.log_error(f"Error creating Modelo 145: {error_msg}\n{error_trace}", "Modelo 145 Error")
        frappe.throw(_(f"Error al crear el Modelo 145: {error_msg}"))
