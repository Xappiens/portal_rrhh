# Copyright (c) 2025, Grupo ATU and contributors
# Endpoint para servir los ítems del sidebar del portal RRHH desde el DocType
# "Portal HR Settings", filtrando por roles.

from __future__ import annotations

import frappe
from frappe import _  # noqa: F401


@frappe.whitelist()
def get_sidebar_items():
    """Devuelve los ítems de sidebar visibles para el usuario actual.
    
    Lee la configuración desde 'Portal HR Settings'.
    """
    settings = frappe.get_cached_doc("Portal HR Settings")
    user_roles = set(frappe.get_roles())
    
    # Check app configurations
    app_config = {
        "app_name": settings.app_name,
        "app_route": settings.app_route,
        "app_icon": settings.app_icon,
        "app_logo": settings.app_logo
    }
    
    visible_items = []
    
    for item in settings.sidebar_items:
        # Check permission
        if item.role and item.role not in user_roles:
            continue
            
        visible_items.append({
            "title": item.title,
            "path": item.route, # frontend expects 'path' or 'to'? current vue uses 'path' prop mapping to 'to'
            "icon": item.icon,
            "section": item.section,
            "role": item.role
        })

    return {
        "app_config": app_config,
        "items": visible_items
    }
