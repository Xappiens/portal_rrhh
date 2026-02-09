# -*- coding: utf-8 -*-
# Copyright (c) 2026, Grupo ATU and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today, getdate
from datetime import datetime, time

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
	resumen = {
		'total_docentes': len(set(p['employee'] for p in previsiones)),
		'total_liquidaciones': len(previsiones),
		'total_horas': sum(flt(p['total_horas']) for p in previsiones),
		'total_bruto': sum(flt(p['bruto']) for p in previsiones),
		'total_ss': sum(flt(p['importe_ss']) for p in previsiones),
		'total_pagar': sum(flt(p['total']) for p in previsiones)
	}
	
	return {
		'previsiones': previsiones,
		'resumen': resumen
	}


@frappe.whitelist()
def crear_liquidaciones_mes(mes, año, liquidaciones_data):
	"""
	Crea las liquidaciones para el mes seleccionado.
	"""
	import json
	
	if isinstance(liquidaciones_data, str):
		liquidaciones_data = json.loads(liquidaciones_data)
	
	año = int(año)
	creadas = 0
	errores = []
	
	for liq_data in liquidaciones_data:
		try:
			# Verificar si ya existe
			existing = frappe.db.exists("Liquidacion Nomina", {
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
			doc = frappe.new_doc("Liquidacion Nomina")
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
	
	# Filtro de employee - búsqueda parcial por nombre o ID
	if employee:
		filters["employee"] = ["like", f"%{employee}%"]
	
	# Filtro de course - búsqueda parcial
	if course:
		filters["course"] = ["like", f"%{course}%"]
	
	if estado:
		filters["estado"] = estado
	
	liquidaciones = frappe.get_all("Liquidacion Nomina",
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
	resumen = {
		'total_docentes': len(set(liq.employee for liq in liquidaciones)),
		'total_liquidaciones': len(liquidaciones),
		'total_horas': sum(flt(liq.total_horas) for liq in liquidaciones),
		'total_bruto': sum(flt(liq.bruto) for liq in liquidaciones),
		'total_ss': sum(flt(liq.importe_ss) for liq in liquidaciones),
		'total_pagar': sum(flt(liq.total) for liq in liquidaciones)
	}
	
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
	doc = frappe.get_doc("Liquidacion Nomina", liquidacion_id)
	
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
	import json
	
	if isinstance(liquidaciones_ids, str):
		liquidaciones_ids = json.loads(liquidaciones_ids)
	
	fecha_envio = today()
	actualizadas = 0
	
	for liq_id in liquidaciones_ids:
		try:
			doc = frappe.get_doc("Liquidacion Nomina", liq_id)
			
			if doc.docstatus != 1:
				continue
			
			doc.estado = "Enviado a Asesoría"
			doc.fecha_envio_asesoria = fecha_envio
			doc.save()
			actualizadas += 1
			
		except Exception as e:
			frappe.log_error(f"Error marcando como enviado {liq_id}: {str(e)}")
	
	return {
		'success': True,
		'actualizadas': actualizadas,
		'message': _("Se marcaron {0} liquidaciones como enviadas").format(actualizadas)
	}


@frappe.whitelist()
def marcar_como_pagado(liquidaciones_ids, fecha_pago=None):
	"""
	Marca las liquidaciones como pagadas.
	"""
	import json
	
	if isinstance(liquidaciones_ids, str):
		liquidaciones_ids = json.loads(liquidaciones_ids)
	
	if not fecha_pago:
		fecha_pago = today()
	
	actualizadas = 0
	
	for liq_id in liquidaciones_ids:
		try:
			doc = frappe.get_doc("Liquidacion Nomina", liq_id)
			
			if doc.docstatus != 1:
				continue
			
			doc.estado = "Pagado"
			doc.fecha_pago = fecha_pago
			doc.save()
			actualizadas += 1
			
		except Exception as e:
			frappe.log_error(f"Error marcando como pagado {liq_id}: {str(e)}")
	
	return {
		'success': True,
		'actualizadas': actualizadas,
		'message': _("Se marcaron {0} liquidaciones como pagadas").format(actualizadas)
	}


@frappe.whitelist()
def generar_reporte_excel(mes, año, liquidaciones_ids=None):
	"""
	Genera el reporte Excel para enviar a la asesoría.
	"""
	import json
	
	if isinstance(liquidaciones_ids, str):
		liquidaciones_ids = json.loads(liquidaciones_ids)
	
	# TODO: Implementar generación de Excel con openpyxl
	# Por ahora, retornar los datos para que el frontend los maneje
	
	filters = {
		"mes": mes,
		"año": int(año),
		"docstatus": 1
	}
	
	if liquidaciones_ids:
		filters["name"] = ["in", liquidaciones_ids]
	
	liquidaciones = frappe.get_all("Liquidacion Nomina",
		filters=filters,
		fields="*",
		order_by="company asc, employee_name asc"
	)
	
	return {
		'success': True,
		'liquidaciones': liquidaciones,
		'mes': mes,
		'año': año
	}


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
		'precio_hora_extra': precio_hora * 1.2,
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


def calcular_horas_mes_desde_calendario(course_name, mes, año):
	"""
	Calcula las horas lectivas de un mes desde el calendario del curso.
	"""
	course = frappe.get_doc('Course', course_name)
	
	if not course.custom_calendario_curso:
		return None
	
	# Mapeo de meses
	month_map = {
		'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
		'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
		'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
	}
	
	mes_num = month_map.get(mes, 0)
	if not mes_num:
		return None
	
	total_horas = 0
	dias_trabajados = set()
	
	# Iterar sobre el calendario
	for cal in course.custom_calendario_curso:
		# Verificar que sea del mes y año correcto
		if cal.fecha and cal.fecha.month == mes_num and cal.fecha.year == año:
			# Solo contar días lectivos
			if cal.lectivo:
				# Calcular horas del día sumando todos los tramos
				horas_dia = 0
				
				tramos = [
					(cal.inicio_primer_tramohorario, cal.fin_primer_tramohorario),
					(cal.inicio_segundo_tramohorario, cal.fin_segundotramohorario),
					(cal.inicio_tercer_tramohorario, cal.fin_tercer_tramohorario),
					(cal.inicio_cuarto_tramohorario, cal.fin_cuarto_tramohorario),
					(cal.inicio_quinto_tramohorario, cal.fin_quinto_tramohorario),
					(cal.inicio_sexto_tramohorario, cal.fin_sexto_tramohorario)
				]
				
				for inicio, fin in tramos:
					if inicio and fin:
						# Convertir a time si es necesario
						from datetime import timedelta
						
						# Si es timedelta (duración), convertir a horas directamente
						if isinstance(inicio, timedelta):
							inicio_horas = inicio.total_seconds() / 3600
						elif isinstance(inicio, str):
							inicio_time = datetime.strptime(inicio, '%H:%M:%S').time()
							inicio_horas = inicio_time.hour + inicio_time.minute / 60 + inicio_time.second / 3600
						elif isinstance(inicio, time):
							inicio_horas = inicio.hour + inicio.minute / 60 + inicio.second / 3600
						else:
							continue
						
						if isinstance(fin, timedelta):
							fin_horas = fin.total_seconds() / 3600
						elif isinstance(fin, str):
							fin_time = datetime.strptime(fin, '%H:%M:%S').time()
							fin_horas = fin_time.hour + fin_time.minute / 60 + fin_time.second / 3600
						elif isinstance(fin, time):
							fin_horas = fin.hour + fin.minute / 60 + fin.second / 3600
						else:
							continue
						
						# Calcular diferencia en horas
						horas = abs(fin_horas - inicio_horas)
						horas_dia += horas
				
				total_horas += horas_dia
				dias_trabajados.add(cal.fecha)
	
	return {
		'total_horas': round(total_horas, 2),
		'dias_trabajados': len(dias_trabajados)
	}


def get_job_offers_docentes(employee=None):
	"""Obtener Job Offers activos de Docentes/Tutores"""
	# Filtro de employee - búsqueda parcial por ID o nombre
	employee_filter = ""
	if employee:
		employee_filter = f"AND (emp.name LIKE '%{employee}%' OR emp.employee_name LIKE '%{employee}%')"
	
	job_offers = frappe.db.sql(f"""
		SELECT 
			jo.name,
			jo.applicant_name,
			jo.custom_dninie,
			jo.company,
			jo.custom_precio_por_hora as precio_hora,
			emp.name as employee,
			emp.employee_name,
			emp.custom_dninie as dni_nie,
			emp.designation
		FROM `tabJob Offer` jo
		INNER JOIN `tabEmployee` emp ON jo.custom_dninie = emp.custom_dninie
		WHERE jo.status = 'Accepted'
		AND jo.docstatus = 1
		AND jo.custom_precio_por_hora > 0
		AND emp.designation IN ('Docente', 'Tutor/a')
		{employee_filter}
	""", as_dict=True)
	
	return job_offers


def get_modificaciones_docentes(employee=None):
	"""Obtener Modificaciones RRHH activas de Docentes/Tutores"""
	# Filtro de employee - búsqueda parcial por ID o nombre
	employee_filter = ""
	if employee:
		employee_filter = f"AND (emp.name LIKE '%{employee}%' OR emp.employee_name LIKE '%{employee}%')"
	
	modificaciones = frappe.db.sql(f"""
		SELECT 
			mr.name,
			mr.employee,
			mr.applicant_name,
			mr.company,
			mr.custom_precio_por_hora as precio_hora,
			emp.employee_name,
			emp.custom_dninie as dni_nie,
			emp.designation
		FROM `tabModificaciones RRHH` mr
		INNER JOIN `tabEmployee` emp ON mr.employee = emp.name
		WHERE mr.status = 'Accepted'
		AND mr.docstatus = 1
		AND mr.custom_precio_por_hora > 0
		AND emp.designation IN ('Docente', 'Tutor/a')
		{employee_filter}
	""", as_dict=True)
	
	return modificaciones


def get_courses_from_job_offer(job_offer_name):
	"""Obtener courses de un Job Offer"""
	courses = frappe.db.sql("""
		SELECT course
		FROM `tabJob Offer Course`
		WHERE parent = %(job_offer)s
		AND course IS NOT NULL
		AND course != ''
	""", {"job_offer": job_offer_name}, as_list=True)
	
	return [c[0] for c in courses if c[0]]


def get_courses_from_modificacion(modificacion_name):
	"""Obtener courses de una Modificación RRHH"""
	# Intentar con diferentes nombres de tabla hija
	tables_to_try = [
		"Modificaciones RRHH Course",
		"Job Offer Course"  # Por si usa la misma tabla
	]
	
	for table_name in tables_to_try:
		try:
			courses = frappe.db.sql(f"""
				SELECT course
				FROM `tab{table_name}`
				WHERE parent = %(modificacion)s
				AND course IS NOT NULL
				AND course != ''
			""", {"modificacion": modificacion_name}, as_list=True)
			
			if courses:
				return [c[0] for c in courses if c[0]]
		except:
			continue
	
	return []
