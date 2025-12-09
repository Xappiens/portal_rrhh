import frappe
from frappe import _
from frappe.utils import today, getdate

@frappe.whitelist(allow_guest=False)
def get_employees_list(filters=None, limit=20, offset=0, search_term=None):
    """
    Get list of employees for the portal
    """
    try:
        frappe.log_error(f"Searching employees: term={search_term}, user={frappe.session.user}", "Debug Employee Search")
        # Verificar primero si el usuario tiene permisos de lectura en Employee
        # Si no tiene permisos básicos, devolver lista vacía
        try:
            meta = frappe.get_meta("Employee")
            role_permissions = frappe.permissions.get_role_permissions(meta, user=frappe.session.user)
            if not role_permissions.get("read") and not role_permissions.get("select"):
                # No tiene permisos básicos de lectura, devolver lista vacía
                return {
                    "employees": [],
                    "total_count": 0,
                    "has_more": False
                }
        except Exception:
            # Si hay error verificando permisos, continuar pero filtrar después
            pass
        
        # Default filters: no status restriction to allow active/inactive employees
        default_filters = {}

        # Merge with provided filters
        if filters:
            if isinstance(filters, str):
                import json
                filters = json.loads(filters)
            default_filters.update(filters)

        # Build OR filters for search
        or_filters = None
        if search_term:
            or_filters = {
                "employee_name": ["like", f"%{search_term}%"],
                "personal_email": ["like", f"%{search_term}%"],
                "company_email": ["like", f"%{search_term}%"],
                "custom_dninie": ["like", f"%{search_term}%"],
                "attendance_device_id": ["like", f"%{search_term}%"],
                "name": ["like", f"%{search_term}%"],
                "user_id": ["like", f"%{search_term}%"],
                "first_name": ["like", f"%{search_term}%"],
                "last_name": ["like", f"%{search_term}%"]
            }

        # Determinar el page_length: si hay búsqueda, traer todo el universo de coincidencias
        page_length = None if search_term else limit

        # Usar frappe.get_list que respeta permisos automáticamente
        employees = frappe.get_list(
            "Employee",
            filters=default_filters,
            or_filters=or_filters,
            fields=[
                "name",
                "employee_name",
                "first_name",
                "last_name",
                "department",
                "designation",
                "image",
                "status",
                "date_of_joining",
                "cell_number",
                "personal_email",
                "company_email",
                "custom_dninie",
                "attendance_device_id"
            ],
            limit_page_length=page_length,
            limit_start=offset if page_length else 0,
            order_by="employee_name asc",
            ignore_permissions=True
        )

        # Filtrar adicionalmente por permisos específicos de cada documento
        # Esto es necesario porque frappe.get_list puede devolver documentos si el usuario
        # tiene permisos generales en el DocType, pero debemos verificar permisos específicos
        filtered_employees = []
        for emp in employees:
            try:
                # Verificar permisos de lectura específicos para este empleado
                if frappe.has_permission("Employee", "read", emp.get('name')):
                    filtered_employees.append(emp)
            except (frappe.PermissionError, frappe.DoesNotExistError):
                # Si no tiene permisos o el documento no existe, omitir
                continue
            except Exception:
                # Si hay algún error, verificar usando get_doc_permissions
                try:
                    emp_doc = frappe.get_doc("Employee", emp.get('name'))
                    perms = frappe.permissions.get_doc_permissions(emp_doc)
                    if perms.get("read"):
                        filtered_employees.append(emp)
                except:
                    continue
        
        employees = filtered_employees

        # Para el conteo total, también usar get_list y filtrar por permisos
        total_employees = frappe.get_list(
            "Employee",
            filters=default_filters,
            or_filters=or_filters,
            fields=["name"],
            limit_page_length=None,
            ignore_permissions=True
        )
        
        # Filtrar el conteo total también por permisos
        total_filtered = []
        for emp in total_employees:
            try:
                if frappe.has_permission("Employee", "read", emp.get('name')):
                    total_filtered.append(emp)
            except:
                continue
        
        total_count = len(total_filtered)

        # Format the data
        for employee in employees:
            # Get user email if available
            if employee.get("user_id"):
                user_email = frappe.db.get_value("User", employee["user_id"], "email")
                if user_email:
                    employee["email"] = user_email
                else:
                    employee["email"] = employee.get("company_email") or employee.get("personal_email")
            else:
                employee["email"] = employee.get("company_email") or employee.get("personal_email")

            # Set avatar
            if employee.get("image"):
                employee["avatar"] = employee["image"]
            else:
                employee["avatar"] = "/assets/frappe/images/default-avatar.png"

            # Format date
            if employee.get("date_of_joining"):
                employee["date_of_joining_formatted"] = frappe.utils.formatdate(employee["date_of_joining"])

        frappe.log_error(f"Search Result: found={len(employees)}, total={total_count}", "Debug Employee Search")
        return {
            "employees": employees,
            "total_count": total_count,
            "has_more": (offset + len(employees)) < total_count
        }

    except Exception as e:
        frappe.log_error(f"Error getting employees: {str(e)}")
        frappe.throw(_("Error getting employees: {0}").format(str(e)))

@frappe.whitelist(allow_guest=False)
def get_departments_list():
    """
    Get list of departments
    """
    try:
        departments = frappe.get_all("Department",
            fields=["name", "department_name"],
            filters={"is_group": 0},
            order_by="department_name asc"
        )

        return departments

    except Exception as e:
        frappe.log_error(f"Error getting departments: {str(e)}")
        frappe.throw(_("Error getting departments: {0}").format(str(e)))

@frappe.whitelist(allow_guest=False)
def get_rrhh_dashboard_stats():
    """
    Get dashboard statistics for RRHH department
    Identifies problems, missing data, and inconsistencies
    """
    try:
        today_date = today()
        today_dt = getdate(today_date)
        
        stats = {
            "employees_missing_data": [],
            "job_offers_expired_active": [],
            "modificaciones_expired_active": [],
            "job_offers_baja_modificaciones_alta": [],
            "summary": {
                "total_employees": 0,
                "employees_missing_data_count": 0,
                "job_offers_expired_active_count": 0,
                "modificaciones_expired_active_count": 0,
                "job_offers_baja_modificaciones_alta_count": 0
            }
        }
        
        # 1. Empleados sin datos personales importantes
        employees = []
        if frappe.has_permission("Employee", "read"):
            employees = frappe.get_list(
                "Employee",
                filters={"status": "Active"},
                fields=[
                    "name",
                    "employee_name",
                    "custom_dninie",
                    "cell_number",
                    "personal_email",
                    "company_email",
                    "custom_no_seguridad_social",
                    "department",
                    "designation"
                ]
            )
        
        stats["summary"]["total_employees"] = len(employees)
        
        for emp in employees:
            missing_fields = []
            if not emp.get("custom_dninie"):
                missing_fields.append("DNI/NIE")
            if not emp.get("cell_number"):
                missing_fields.append("Teléfono")
            if not emp.get("personal_email") and not emp.get("company_email"):
                missing_fields.append("Email")
            if not emp.get("custom_no_seguridad_social"):
                missing_fields.append("Número Seguridad Social")
            
            if missing_fields:
                stats["employees_missing_data"].append({
                    "employee_name": emp.name,
                    "employee_display_name": emp.employee_name or emp.name,
                    "department": emp.department or "Sin departamento",
                    "designation": emp.designation or "Sin cargo",
                    "missing_fields": missing_fields,
                    "missing_count": len(missing_fields)
                })
        
        stats["summary"]["employees_missing_data_count"] = len(stats["employees_missing_data"])
        
        # 2. Job Offers con fecha fin vencida pero workflow_state = "Alta"
        # 2. Job Offers con fecha fin vencida pero workflow_state = "Alta"
        job_offers = []
        try:
            if frappe.has_permission("Job Offer", "read"):
                job_offers = frappe.get_list(
                    "Job Offer",
                    filters={
                        "docstatus": 1,
                        "workflow_state": "Alta"
                    },
                    fields=[
                        "name",
                        "applicant_name",
                        "custom_dninie",
                        "custom_fecha_fin",
                        "workflow_state",
                        "designation",
                        "company"
                    ]
                )
        except frappe.PermissionError:
            job_offers = []
        
        for jo in job_offers:
            if jo.get("custom_fecha_fin"):
                fecha_fin = getdate(jo["custom_fecha_fin"])
                if fecha_fin < today_dt:
                    # Buscar empleado relacionado por DNI
                    employee_name = None
                    if jo.get("custom_dninie"):
                        employee = frappe.db.get_value("Employee",
                            {"custom_dninie": jo["custom_dninie"], "status": "Active"},
                            "name"
                        )
                        if employee:
                            employee_name = employee
                    
                    stats["job_offers_expired_active"].append({
                        "job_offer_name": jo.name,
                        "applicant_name": jo.applicant_name or "N/A",
                        "employee_name": employee_name,
                        "custom_dninie": jo.custom_dninie or "N/A",
                        "fecha_fin": jo.custom_fecha_fin,
                        "dias_vencido": (today_dt - fecha_fin).days,
                        "designation": jo.designation or "N/A",
                        "company": jo.company or "N/A"
                    })
        
        stats["summary"]["job_offers_expired_active_count"] = len(stats["job_offers_expired_active"])
        
        # 3. Modificaciones RRHH con fecha fin vencida pero workflow_state = "Alta"
        modificaciones = []
        try:
            if frappe.has_permission("Modificaciones RRHH", "read"):
                modificaciones = frappe.get_list(
                    "Modificaciones RRHH",
                    filters={
                        "docstatus": 1,
                        "workflow_state": "Alta"
                    },
                    fields=[
                        "name",
                        "employee",
                        "end_date",
                        "workflow_state",
                        "designation",
                        "company",
                        "tipo_actualizacion",
                        "job_offer"
                    ]
                )
        except frappe.PermissionError:
            modificaciones = []
        
        for mod in modificaciones:
            if mod.get("end_date"):
                fecha_fin = getdate(mod["end_date"])
                if fecha_fin < today_dt:
                    employee_name = None
                    employee_display_name = None
                    if mod.get("employee"):
                        employee_display_name = frappe.db.get_value("Employee",
                            mod["employee"],
                            "employee_name"
                        )
                        employee_name = mod["employee"]
                    
                    stats["modificaciones_expired_active"].append({
                        "modificacion_name": mod.name,
                        "employee_name": employee_name,
                        "employee_display_name": employee_display_name or "N/A",
                        "end_date": mod.end_date,
                        "dias_vencido": (today_dt - fecha_fin).days,
                        "designation": mod.designation or "N/A",
                        "company": mod.company or "N/A",
                        "tipo_actualizacion": mod.tipo_actualizacion or "N/A",
                        "job_offer": mod.job_offer or "N/A"
                    })
        
        stats["summary"]["modificaciones_expired_active_count"] = len(stats["modificaciones_expired_active"])
        
        # 4. Job Offers en "Baja" pero con Modificaciones RRHH relacionadas en "Alta"
        # 4. Job Offers en "Baja" pero con Modificaciones RRHH relacionadas en "Alta"
        job_offers_baja = []
        try:
            if frappe.has_permission("Job Offer", "read"):
                job_offers_baja = frappe.get_list(
                    "Job Offer",
                    filters={
                        "docstatus": 1,
                        "workflow_state": "Baja"
                    },
                    fields=["name", "applicant_name", "custom_dninie", "designation", "company"]
                )
        except frappe.PermissionError:
            job_offers_baja = []
        
        for jo_baja in job_offers_baja:
            # Buscar modificaciones RRHH relacionadas que estén en "Alta"
            modificaciones_alta = []
            try:
                if frappe.has_permission("Modificaciones RRHH", "read"):
                    modificaciones_alta = frappe.get_list(
                        "Modificaciones RRHH",
                        filters={
                            "docstatus": 1,
                            "workflow_state": "Alta",
                            "job_offer": jo_baja.name
                        },
                        fields=["name", "employee", "tipo_actualizacion", "start_date", "end_date"]
                    )
            except frappe.PermissionError:
                modificaciones_alta = []
            
            if modificaciones_alta:
                employee_name = None
                employee_display_name = None
                if modificaciones_alta[0].get("employee"):
                    employee_display_name = frappe.db.get_value("Employee",
                        modificaciones_alta[0]["employee"],
                        "employee_name"
                    )
                    employee_name = modificaciones_alta[0]["employee"]
                
                stats["job_offers_baja_modificaciones_alta"].append({
                    "job_offer_name": jo_baja.name,
                    "job_offer_state": "Baja",
                    "applicant_name": jo_baja.applicant_name or "N/A",
                    "employee_name": employee_name,
                    "employee_display_name": employee_display_name or "N/A",
                    "custom_dninie": jo_baja.custom_dninie or "N/A",
                    "designation": jo_baja.designation or "N/A",
                    "company": jo_baja.company or "N/A",
                    "modificaciones_count": len(modificaciones_alta),
                    "modificaciones": [
                        {
                            "name": m.name,
                            "tipo_actualizacion": m.tipo_actualizacion or "N/A",
                            "start_date": m.start_date,
                            "end_date": m.end_date
                        }
                        for m in modificaciones_alta
                    ]
                })
        
        stats["summary"]["job_offers_baja_modificaciones_alta_count"] = len(stats["job_offers_baja_modificaciones_alta"])
        
        # Ordenar por severidad (más problemas primero)
        stats["employees_missing_data"].sort(key=lambda x: x["missing_count"], reverse=True)
        stats["job_offers_expired_active"].sort(key=lambda x: x["dias_vencido"], reverse=True)
        stats["modificaciones_expired_active"].sort(key=lambda x: x["dias_vencido"], reverse=True)
        
        return stats
        
    except Exception as e:
        frappe.log_error(f"Error getting RRHH dashboard stats: {str(e)}")
        frappe.throw(_("Error getting dashboard statistics: {0}").format(str(e)))
