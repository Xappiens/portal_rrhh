# Port of existing sidebar items to Portal HR Settings
import frappe

def run():
    # 1. Fetch existing Sidebar Items from the old DocType
    old_items = frappe.get_all("Sidebar Item", fields=["title", "path", "icon", "order", "name"])
    
    # 2. Define Section Mapping (based on seed_sidebar_items.py logic/grouping)
    # The seed script had sections implied by comments or hardcoded in frontend.
    # We will try to map them logically.
    
    section_map = {
        "AttendanceReport": "Configuración",
        "Departamentos": "Configuración",
        "Configuracion": "Configuración",
        "Configuración General": "Configuración",
        
        # Everything else defaults to General or management
        "RecruitmentReports": "Reclutamiento",
        "CVAnalysis": "Reclutamiento",
        "Vacantes": "Reclutamiento",
        "Contratacion": "Reclutamiento",
        "Solicitudes": "Reclutamiento",
        "Evaluaciones": "Reclutamiento",
        
        "AIDashboard": "IA",
        
        "Empleados": "Gestión",
        "Timesheets": "Gestión",
        
        "Profile": "General",
        "Mi Perfil": "General",
        "Fichaje": "General",
        "Vacaciones": "General",
        "SpanishLeave": "General",
        "AttendanceAnomalies": "General",
    }

    # Helper to resolve icon if missing (from frontend iconMap)
    icon_map = {
        "Profile": "user",
        "Contratacion": "briefcase",
        "Empleados": "users",
        "Timesheets": "calendar",
        "Vacantes": "briefcase",
        "Solicitudes": "file-text",
        "Evaluaciones": "clipboard",
        "Reportes": "bar-chart-2",
        "AIDashboard": "cpu",
        "CVAnalysis": "search",
        "RecruitmentReports": "pie-chart",
        "AttendanceReport": "file-text",
        "Departamentos": "layers",
        "Configuracion": "settings",
        "Fichaje": "clock",
        "SpanishLeave": "sun",
        "AttendanceAnomalies": "alert-circle"
    }

    items_to_add = []
    
    # Sort by order to maintain sequence
    old_items.sort(key=lambda x: x.order or 999)

    for item in old_items:
        # Resolve Section
        section = section_map.get(item.path, "General") 
        # Fallback if mapped by title
        if section == "General":
             section = section_map.get(item.title, "General")

        # Resolve Icon
        icon = item.icon
        if not icon or icon == "NULL":
            icon = icon_map.get(item.path, "circle")

        items_to_add.append({
            "title": item.title,
            "route": item.path,
            "icon": icon,
            "section": section,
            "role": None # We don't have role info easily mapable from old child table without complex query, will leave empty for now as most were public/auth required
        })

    # 3. Create/Update Portal HR Settings
    settings = frappe.get_doc("Portal HR Settings")
    settings.app_name = "Portal RRHH"
    settings.sidebar_items = [] # clear existing if any to avoid dups on re-run or just append? Let's overwrite to be clean migration.
    
    for i in items_to_add:
        settings.append("sidebar_items", i)
        
    settings.save()
    frappe.db.commit()
    print("Portal HR Settings populated with {} items.".format(len(items_to_add)))

if __name__ == "__main__":
    run()
