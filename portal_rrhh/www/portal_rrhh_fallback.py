import frappe
from frappe import _

def get_context(context):
    """Fallback handler for all portal_rrhh routes"""
    context.title = "Portal RRHH"
    context.no_cache = 1

    # Get the current path
    path = frappe.local.request.path

    # Extract the page from the path
    if path.startswith('/portal-rrhh/'):
        page = path.split('/')[-1]
        if page in ['dashboard', 'empleados', 'vacantes', 'solicitudes', 'evaluaciones', 'reportes']:
            context.current_page = page
        else:
            context.current_page = 'dashboard'
    else:
        context.current_page = 'dashboard'

    context.app_name = "portal_rrhh"

    return context
