# -*- coding: utf-8 -*-
# Copyright (c) 2026, Grupo ATU and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today, getdate
import json

# Importar funciones compartidas del DocType
from hrms_integrations.hrms_integrations.doctype.liquidacion_nomina.liquidacion_nomina import (
	calcular_horas_mes_desde_calendario,
	get_job_offers_docentes,
	get_modificaciones_docentes,
	get_courses_from_job_offer,
	get_courses_from_modificacion,
	MONTH_MAP
)

DOCTYPE_NAME = "Liquidacion Nomina"


@frappe.whitelist()
def get_prevision_mes(mes, año, employee=None, course=None):
	"""
	Obtiene la previsión de liquidaciones para un mes específico.
	Calcula en tiempo real desde Job Offers y Modificaciones RRHH activos.
	"""
	año = int(año)
	previsiones = []
	
	# Obtener Job Offers activos de Docentes/Tutores
	job_offers = get_job_offers_docentes(employee)
	
	for jo in job_offers:
		# Obtener courses del Job Offer
		courses = get_courses_from_job_offer(jo.name)
		
		for course_name in courses:
			# Filtrar por course si se especificó (búsqueda parcial)
			if course and course.lower() not in course_name.lower():
				continue
			
			# Verificar si ya existe liquidación
			existing = frappe.db.exists(DOCTYPE_NAME, {
				"employee": jo.employee,
				"course": course_name,
				"mes": mes,
				"año": año,
				"docstatus": ["!=", 2]
			})
			
			if existing:
				continue  # Ya existe, no mostrar en previsión
			
			# Calcular previsión
			prevision = calcular_prevision_liquidacion(
				employee=jo.employee,
				employee_name=jo.employee_name,
				dni_nie=jo.dni_nie,
				designation=jo.designation,
				company=jo.company,
				source_type="Job Offer",
				source_doc=jo.name,
				course=course_name,
				mes=mes,
				año=año,
				precio_hora=jo.precio_hora
			)
			
			if prevision:
				previsiones.append(prevision)
	
	# Obtener Modificaciones RRHH activas
	modificaciones = get_modificaciones_docentes(employee)
	
	for mod in modificaciones:
		# Obtener courses de la Modificación
		courses = get_courses_from_modificacion(mod.name)
		
		for course_name in courses:
			# Filtrar por course si se especificó (búsqueda parcial)
			if course and course.lower() not in course_name.lower():
				continue
			
			# Verificar si ya existe liquidación
			existing = frappe.db.exists(DOCTYPE_NAME, {
				"employee": mod.employee,
				"course": course_name,
				"mes": mes,
				"año": año,
				"docstatus": ["!=", 2]
			})
			
			if existing:
				continue  # Ya existe, no mostrar en previsión
			
			# Calcular previsión
			prevision = calcular_prevision_liquidacion(
				employee=mod.employee,
				employee_name=mod.employee_name,
				dni_nie=mod.dni_nie,
				designation=mod.designation,
				company=mod.company,
				source_type="Modificaciones RRHH",
				source_doc=mod.name,
				course=course_name,
				mes=mes,
				año=año,
				precio_hora=mod.precio_hora
			)
			
			if prevision:
				previsiones.append(prevision)
	
	# Calcular resumen
	resumen = calcular_resumen(previsiones)
	
	return {
		'previsiones': previsiones,
		'resumen': resumen
	}


@frappe.whitelist()
def crear_liquidaciones_mes(mes, año, liquidaciones_data):
	"""
	Crea las liquidaciones para el mes seleccionado.
	"""
	if isinstance(liquidaciones_data, str):
		liquidaciones_data = json.loads(liquidaciones_data)
	
	año = int(año)
	creadas = 0
	errores = []
	
	for liq_data in liquidaciones_data:
		try:
			# Verificar si ya existe
			existing = frappe.db.exists(DOCTYPE_NAME, {
				"employee": liq_data['employee'],
				"course": liq_data['course'],
				"mes": mes,
				"año": año,
				"docstatus": ["!=", 2]
			})
			
			if existing:
				errores.append(f"{liq_data['employee_name']}: Ya existe liquidación")
				continue
			
			# Crear liquidación
			doc = frappe.new_doc(DOCTYPE_NAME)
			doc.employee = liq_data['employee']
			doc.mes = mes
			doc.año = año
			doc.company = liq_data['company']
			doc.source_document_type = liq_data['source_type']
			doc.source_document = liq_data['source_doc']
			doc.course = liq_data['course']
			doc.precio_hora = liq_data['precio_hora']
			doc.horas_extras = flt(liq_data.get('horas_extras', 0))
			doc.precio_hora_extra = flt(liq_data.get('precio_hora_extra', 0))
			doc.es_ultimo_mes = liq_data.get('es_ultimo_mes', 0)
			doc.estado = "Liquidado"
			
			doc.insert()
			doc.submit()
			creadas += 1
			
		except Exception as e:
			errores.append(f"{liq_data.get('employee_name', 'Unknown')}: {str(e)}")
			frappe.log_error(f"Error creando liquidación: {str(e)}", "Crear Liquidación")
	
	return {
		'success': True,
		'creadas': creadas,
		'errores': errores,
		'message': _("Se crearon {0} liquidaciones").format(creadas)
	}


@frappe.whitelist()
def get_liquidaciones_mes(mes, año, employee=None, course=None, estado=None):
	"""
	Obtiene las liquidaciones ya creadas para un mes.
	"""
	filters = {
		"mes": mes,
		"año": int(año)
	}
	
	if estado:
		filters["estado"] = estado
	
	liquidaciones = frappe.get_all(DOCTYPE_NAME,
		filters=filters,
		fields=[
			"name", "employee", "employee_name", "dni_nie", "designation",
			"course", "company", "mes", "año",
			"horas_normales", "horas_extras", "total_horas", "dias_trabajados",
			"precio_hora", "precio_hora_extra",
			"bruto", "vacaciones_mes", "bruto_menos_vacaciones",
			"vacaciones_acumuladas", "base_ss", "importe_ss", "total",
			"estado", "fecha_liquidacion", "fecha_envio_asesoria", "fecha_pago",
			"es_ultimo_mes", "docstatus"
		],
		order_by="employee_name asc, course asc"
	)
	
	# Calcular resumen
	resumen = calcular_resumen(liquidaciones)
	
	return {
		'liquidaciones': liquidaciones,
		'resumen': resumen
	}


@frappe.whitelist()
def actualizar_horas_extras(liquidacion_id, horas_extras, precio_hora_extra=None):
	"""
	Actualiza las horas extras de una liquidación.
	Solo se puede hacer si no está submitted.
	"""
	doc = frappe.get_doc(DOCTYPE_NAME, liquidacion_id)
	
	if doc.docstatus == 1:
		frappe.throw(_("No se pueden modificar liquidaciones ya enviadas"))
	
	doc.horas_extras = flt(horas_extras)
	if precio_hora_extra:
		doc.precio_hora_extra = flt(precio_hora_extra)
	
	doc.save()
	
	return {
		'success': True,
		'message': _("Horas extras actualizadas"),
		'liquidacion': doc.as_dict()
	}


@frappe.whitelist()
def marcar_como_enviado(liquidaciones_ids):
	"""
	Marca las liquidaciones seleccionadas como enviadas a asesoría.
	"""
	if isinstance(liquidaciones_ids, str):
		liquidaciones_ids = json.loads(liquidaciones_ids)
	
	fecha_envio = today()
	actualizadas = 0
	errores = []
	
	for liq_id in liquidaciones_ids:
		try:
			doc = frappe.get_doc(DOCTYPE_NAME, liq_id)
			
			if doc.docstatus != 1:
				errores.append(f"{liq_id}: No está liquidada")
				continue
			
			doc.estado = "Enviado a Asesoría"
			doc.fecha_envio_asesoria = fecha_envio
			doc.save()
			actualizadas += 1
			
		except Exception as e:
			errores.append(f"{liq_id}: {str(e)}")
			frappe.log_error(f"Error marcando como enviado {liq_id}: {str(e)}")
	
	return {
		'success': True,
		'actualizadas': actualizadas,
		'errores': errores,
		'message': _("Se marcaron {0} liquidaciones como enviadas").format(actualizadas)
	}


@frappe.whitelist()
def marcar_como_pagado(liquidaciones_ids, fecha_pago=None):
	"""
	Marca las liquidaciones como pagadas.
	"""
	if isinstance(liquidaciones_ids, str):
		liquidaciones_ids = json.loads(liquidaciones_ids)
	
	if not fecha_pago:
		fecha_pago = today()
	
	actualizadas = 0
	errores = []
	
	for liq_id in liquidaciones_ids:
		try:
			doc = frappe.get_doc(DOCTYPE_NAME, liq_id)
			
			if doc.docstatus != 1:
				errores.append(f"{liq_id}: No está liquidada")
				continue
			
			doc.estado = "Pagado"
			doc.fecha_pago = fecha_pago
			doc.save()
			actualizadas += 1
			
		except Exception as e:
			errores.append(f"{liq_id}: {str(e)}")
			frappe.log_error(f"Error marcando como pagado {liq_id}: {str(e)}")
	
	return {
		'success': True,
		'actualizadas': actualizadas,
		'errores': errores,
		'message': _("Se marcaron {0} liquidaciones como pagadas").format(actualizadas)
	}


@frappe.whitelist()
def generar_reporte_excel(mes, año, liquidaciones_ids=None):
	"""
	Genera el reporte Excel para enviar a la asesoría.
	Devuelve la URL del archivo generado.
	"""
	if isinstance(liquidaciones_ids, str):
		liquidaciones_ids = json.loads(liquidaciones_ids)
	
	filters = {
		"mes": mes,
		"año": int(año),
		"docstatus": 1
	}
	
	if liquidaciones_ids:
		filters["name"] = ["in", liquidaciones_ids]
	
	liquidaciones = frappe.get_all(DOCTYPE_NAME,
		filters=filters,
		fields="*",
		order_by="company asc, employee_name asc"
	)
	
	if not liquidaciones:
		frappe.throw(_("No hay liquidaciones para exportar"))
	
	# Generar Excel
	try:
		from openpyxl import Workbook
		from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
		from openpyxl.utils import get_column_letter
		import io
		
		wb = Workbook()
		ws = wb.active
		ws.title = f"Liquidaciones {mes} {año}"
		
		# Estilos
		header_font = Font(bold=True, color="FFFFFF")
		header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
		header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
		thin_border = Border(
			left=Side(style='thin'),
			right=Side(style='thin'),
			top=Side(style='thin'),
			bottom=Side(style='thin')
		)
		currency_format = '#,##0.00 €'
		
		# Headers
		headers = [
			"Empresa", "Empleado", "DNI/NIE", "Designation", "Course",
			"Horas Normales", "Horas Extras", "Total Horas", "Días Trabajados",
			"Precio/Hora", "Precio/Hora Extra",
			"Bruto", "Vacaciones Mes", "Bruto - Vacaciones",
			"Base SS", "Importe SS", "TOTAL",
			"Estado", "Fecha Liquidación"
		]
		
		for col_num, header in enumerate(headers, 1):
			cell = ws.cell(row=1, column=col_num, value=header)
			cell.font = header_font
			cell.fill = header_fill
			cell.alignment = header_alignment
			cell.border = thin_border
		
		# Datos
		for row_num, liq in enumerate(liquidaciones, 2):
			row_data = [
				liq.company,
				liq.employee_name,
				liq.dni_nie,
				liq.designation,
				liq.course,
				liq.horas_normales,
				liq.horas_extras,
				liq.total_horas,
				liq.dias_trabajados,
				liq.precio_hora,
				liq.precio_hora_extra,
				liq.bruto,
				liq.vacaciones_mes,
				liq.bruto_menos_vacaciones,
				liq.base_ss,
				liq.importe_ss,
				liq.total,
				liq.estado,
				str(liq.fecha_liquidacion) if liq.fecha_liquidacion else ""
			]
			
			for col_num, value in enumerate(row_data, 1):
				cell = ws.cell(row=row_num, column=col_num, value=value)
				cell.border = thin_border
				
				# Formato de moneda para columnas de importes
				if col_num in [10, 11, 12, 13, 14, 15, 16, 17]:
					cell.number_format = currency_format
		
		# Fila de totales
		total_row = len(liquidaciones) + 2
		ws.cell(row=total_row, column=1, value="TOTALES").font = Font(bold=True)
		
		# Sumar columnas numéricas
		sum_columns = {
			6: sum(flt(l.horas_normales) for l in liquidaciones),
			7: sum(flt(l.horas_extras) for l in liquidaciones),
			8: sum(flt(l.total_horas) for l in liquidaciones),
			12: sum(flt(l.bruto) for l in liquidaciones),
			13: sum(flt(l.vacaciones_mes) for l in liquidaciones),
			14: sum(flt(l.bruto_menos_vacaciones) for l in liquidaciones),
			15: sum(flt(l.base_ss) for l in liquidaciones),
			16: sum(flt(l.importe_ss) for l in liquidaciones),
			17: sum(flt(l.total) for l in liquidaciones),
		}
		
		for col, value in sum_columns.items():
			cell = ws.cell(row=total_row, column=col, value=value)
			cell.font = Font(bold=True)
			cell.border = thin_border
			if col >= 10:
				cell.number_format = currency_format
		
		# Ajustar anchos de columna
		column_widths = [15, 25, 12, 15, 30, 12, 12, 12, 12, 12, 12, 12, 12, 15, 12, 12, 12, 15, 15]
		for i, width in enumerate(column_widths, 1):
			ws.column_dimensions[get_column_letter(i)].width = width
		
		# Guardar en buffer
		output = io.BytesIO()
		wb.save(output)
		output.seek(0)
		
		# Guardar como archivo en Frappe
		filename = f"Liquidaciones_{mes}_{año}.xlsx"
		file_doc = frappe.get_doc({
			"doctype": "File",
			"file_name": filename,
			"content": output.getvalue(),
			"is_private": 1
		})
		file_doc.save(ignore_permissions=True)
		
		return {
			'success': True,
			'file_url': file_doc.file_url,
			'filename': filename,
			'message': _("Reporte generado correctamente")
		}
		
	except ImportError:
		frappe.throw(_("El módulo openpyxl no está instalado. Ejecute: pip install openpyxl"))
	except Exception as e:
		frappe.log_error(f"Error generando Excel: {str(e)}", "Generar Reporte Excel")
		frappe.throw(_("Error generando el reporte: {0}").format(str(e)))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calcular_prevision_liquidacion(employee, employee_name, dni_nie, designation, company,
									source_type, source_doc, course, mes, año, precio_hora):
	"""
	Calcula la previsión de liquidación para un empleado/course/mes.
	"""
	# 1. Calcular horas desde el calendario
	horas_data = calcular_horas_mes_desde_calendario(course, mes, año)
	
	if not horas_data or horas_data['total_horas'] == 0:
		return None
	
	horas_normales = horas_data['total_horas']
	dias_trabajados = horas_data['dias_trabajados']
	
	# 2. Calcular importes
	importe_horas_normales = horas_normales * flt(precio_hora)
	bruto = importe_horas_normales
	
	# 3. Calcular vacaciones (8.33%)
	vacaciones_mes = round(bruto * 0.0833, 2)
	
	# 4. Calcular bruto menos vacaciones
	bruto_menos_vacaciones = bruto - vacaciones_mes
	
	# 5. Calcular SS (32.07%)
	importe_ss = round(bruto_menos_vacaciones * 0.3207, 2)
	
	# 6. Calcular total
	total = bruto_menos_vacaciones + importe_ss
	
	return {
		'employee': employee,
		'employee_name': employee_name,
		'dni_nie': dni_nie,
		'designation': designation,
		'company': company,
		'source_type': source_type,
		'source_doc': source_doc,
		'course': course,
		'mes': mes,
		'año': año,
		'horas_normales': horas_normales,
		'horas_extras': 0,
		'total_horas': horas_normales,
		'dias_trabajados': dias_trabajados,
		'precio_hora': precio_hora,
		'precio_hora_extra': round(flt(precio_hora) * 1.2, 2),
		'importe_horas_normales': importe_horas_normales,
		'importe_horas_extras': 0,
		'bruto': bruto,
		'vacaciones_mes': vacaciones_mes,
		'bruto_menos_vacaciones': bruto_menos_vacaciones,
		'vacaciones_acumuladas': 0,
		'base_ss': bruto_menos_vacaciones,
		'importe_ss': importe_ss,
		'total': total,
		'estado': 'Previsión',
		'es_ultimo_mes': 0
	}


def calcular_resumen(items):
	"""Calcula el resumen de una lista de liquidaciones/previsiones"""
	if not items:
		return {
			'total_docentes': 0,
			'total_liquidaciones': 0,
			'total_horas': 0,
			'total_bruto': 0,
			'total_ss': 0,
			'total_pagar': 0
		}
	
	# Obtener employee de cada item (puede ser dict o frappe._dict)
	employees = set()
	for item in items:
		emp = item.get('employee') if isinstance(item, dict) else item.employee
		if emp:
			employees.add(emp)
	
	return {
		'total_docentes': len(employees),
		'total_liquidaciones': len(items),
		'total_horas': sum(flt(item.get('total_horas') if isinstance(item, dict) else item.total_horas) for item in items),
		'total_bruto': sum(flt(item.get('bruto') if isinstance(item, dict) else item.bruto) for item in items),
		'total_ss': sum(flt(item.get('importe_ss') if isinstance(item, dict) else item.importe_ss) for item in items),
		'total_pagar': sum(flt(item.get('total') if isinstance(item, dict) else item.total) for item in items)
	}
