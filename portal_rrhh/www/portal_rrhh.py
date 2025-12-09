# Copyright (c) 2024, Portal RRHH and Contributors
# GNU GPLv3 License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.telemetry import capture

no_cache = 1


def get_context():
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    context = frappe._dict()
    context.boot = get_boot()
    context.boot.csrf_token = csrf_token

    # Get the current path to determine which page to show
    path = frappe.local.request.path

    # Extract page from path
    if path == '/portal-rrhh' or path == '/portal-rrhh/':
        current_page = 'dashboard'
    elif path.startswith('/portal-rrhh/'):
        # Extract the page name from the path
        path_parts = path.split('/')
        if len(path_parts) > 2:
            page_name = path_parts[2]
            # Validate that it's a known page
            valid_pages = ['dashboard', 'contratacion', 'empleados', 'vacantes', 'solicitudes', 'evaluaciones', 'reportes']
            if page_name in valid_pages:
                current_page = page_name
            else:
                current_page = 'dashboard'
        else:
            current_page = 'dashboard'
    else:
        current_page = 'dashboard'

    context.current_page = current_page
    context.app_name = "portal_rrhh"

    if frappe.session.user != "Guest":
        capture("active_site", "portal_rrhh")
    return context


@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
    if not frappe.conf.developer_mode:
        frappe.throw("This method is only meant for developer mode")
    return get_boot()


def get_boot():
    boot = frappe._dict(
        {
            "frappe_version": frappe.__version__,
            "default_route": get_default_route(),
            "site_name": frappe.local.site,
            "read_only_mode": frappe.flags.read_only,
        }
    )
    
    # Agregar información del usuario si está logueado
    if frappe.session.user != "Guest":
        boot.user = frappe.session.user
        boot.user_info = {
            "name": frappe.session.user,
            "full_name": frappe.utils.get_fullname(frappe.session.user),
        }
    
    return boot


def get_default_route():
    return "/portal-rrhh"
