# Copyright (c) 2025, Grupo ATU
#
# Script idempotente para poblar los ítems actuales del sidebar del portal RRHH
# en el DocType "Sidebar Item". No ejecuta migrate; usa insert/update directos.
#
# Uso:
#   bench --site erp.grupoatu.com execute portal_rrhh.scripts.seed_sidebar_items.run

from __future__ import annotations

import frappe


def run():
    # Lista basada en AppSidebar.vue y router.js (rutas reales con prefijo /portal-rrhh)
    # Usamos el nombre de la ruta (router name) para que SidebarLink navegue correctamente
    items = [
        ("Mi Perfil", "Profile", 10),
        ("Contratación", "Contratacion", 20),
        ("Empleados", "Empleados", 30),
        ("Registro de Horas", "Timesheets", 40),
        ("Vacantes", "Vacantes", 50),
        ("Solicitudes", "Solicitudes", 60),
        ("Evaluaciones", "Evaluaciones", 70),
        ("Reportes", "Reportes", 80),
        ("Panel de IA", "AIDashboard", 90),
        ("Análisis de CV", "CVAnalysis", 100),
        ("Reportes de Reclutamiento", "RecruitmentReports", 110),
        # Sección configuración
        ("Reporte Asistencia", "AttendanceReport", 200),
        ("Departamentos", "Departamentos", 210),
        ("Configuración General", "Configuracion", 220),
    ]

    created, updated = [], []

    for title, path, order in items:
        existing_name = frappe.db.exists("Sidebar Item", title)
        if existing_name:
            doc = frappe.get_doc("Sidebar Item", existing_name)
            doc.path = path
            doc.order = order
            doc.enabled = 1
            doc.is_public = 0
            doc.requires_auth = 1
            doc.app_module = "Portal RRHH"
            doc.save(ignore_permissions=True)
            updated.append(title)
        else:
            doc = frappe.get_doc(
                {
                    "doctype": "Sidebar Item",
                    "title": title,
                    "path": path,
                    "order": order,
                    "enabled": 1,
                    "is_public": 0,
                    "requires_auth": 1,
                    "app_module": "Portal RRHH",
                    # roles: se dejan vacíos para que se asignen manualmente
                }
            )
            doc.insert(ignore_permissions=True)
            created.append(title)

    frappe.db.commit()

    frappe.msgprint(
        f"Sidebar Items creados: {created or '0'}. "
        f"Actualizados: {updated or '0'}."
    )

