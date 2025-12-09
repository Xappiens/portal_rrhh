# Copyright (c) 2025, Grupo ATU and contributors
# Endpoint para servir los ítems del sidebar del portal RRHH desde el DocType
# "Sidebar Item", filtrando por roles.

from __future__ import annotations

import frappe
from frappe import _  # noqa: F401
from frappe.utils import cint


@frappe.whitelist()
def get_sidebar_items(app_module: str = "Portal RRHH"):
    """Devuelve los ítems de sidebar visibles para el usuario actual.

    Usamos ignore_permissions=True porque la autorización real se gestiona
    por la tabla hija de roles y flags públicos/autenticación.
    """
    user_roles = set(frappe.get_roles())
    is_guest = frappe.session.user == "Guest"

    docs = frappe.get_all(
        "Sidebar Item",
        filters={
            "enabled": 1,
            "app_module": app_module,
        },
        fields=[
            "name",
            "title",
            "path",
            "icon",
            "order",
            "is_public",
            "requires_auth",
            "feature_flag",
            "parent_item",
        ],
        order_by="`order` asc, `title` asc",
        ignore_permissions=True,
    )

    # Obtener roles de hijos en bloque para eficiencia
    if docs:
        names = [d.name for d in docs]
        child_roles = frappe.get_all(
            "Sidebar Item Role",
            filters={"parent": ("in", names)},
            fields=["parent", "role", "permission"],
            ignore_permissions=True,
        )
    else:
        child_roles = []

    roles_by_parent = {}
    for row in child_roles:
        roles_by_parent.setdefault(row.parent, []).append(row)

    visible = []
    for d in docs:
        # Público
        if cint(d.is_public):
            visible.append(_map_doc(d))
            continue

        # Requiere auth y es guest -> no
        if cint(d.requires_auth) and is_guest:
            continue

        # Evaluar permisos por rol:
        # - Si no hay roles definidos en la tabla hija, se permite a cualquier usuario autenticado.
        # - Si hay roles, se aplica: Hide gana sobre View; View requiere rol coincidente.
        child = roles_by_parent.get(d.name, [])
        if not child:
            visible.append(_map_doc(d))
            continue

        allowed = False
        deny = False
        for r in child:
            if r.role in user_roles:
                if r.permission == "Hide":
                    deny = True
                    break
                if r.permission == "View":
                    allowed = True
        if deny:
            continue
        if allowed:
            visible.append(_map_doc(d))

    return visible


def _map_doc(d):
    return {
        "title": d.title,
        "path": d.path,
        "icon": d.icon,
        "order": d.order,
        "feature_flag": d.feature_flag,
        "parent": d.parent_item,
    }

