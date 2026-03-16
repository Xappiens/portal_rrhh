import frappe
from frappe import _

@frappe.whitelist()
def get_courses_without_instructor():
    """
    Get courses in Previsto or Planificado state that don't have an instructor assigned.
    Used for hiring planning/forecasting.
    """
    # Get all courses in Previsto or Planificado state
    courses = frappe.get_all(
        "Course",
        filters=[["state", "in", ["Previsto", "Planificado"]]],
        fields=[
            "name", "course_name", "state", "start_date", "end_date", "hours",
            "custom_modalidad", "center", "city", "expediente", "code",
            "custom_horas_practicas", "custom_fecha_inicio_practicas", 
            "custom_fecha_fin_practicas", "custom_fecha_fin_teoria",
            "comunidad_autonoma", "custom_pronvincia"
        ],
        order_by="start_date asc",
        ignore_permissions=True
    )
    
    if not courses:
        return []
    
    # Get all course names that have at least one instructor in "Instructor Curso" child table
    # The child table is linked via fieldname "custom_instructor"
    courses_with_instructor = frappe.get_all(
        "Instructor Curso",
        filters=[
            ["instructor", "is", "set"],
            ["parentfield", "=", "custom_instructor"]
        ],
        fields=["parent"],
        ignore_permissions=True
    )
    
    courses_with_instructor_set = set(ci.parent for ci in courses_with_instructor)
    
    # Filter out courses that have instructors
    courses_without_instructor = [
        c for c in courses 
        if c.name not in courses_with_instructor_set
    ]
    
    return courses_without_instructor


@frappe.whitelist()
def get_course_details(course_name):
    """
    Get detailed information about a specific course.
    """
    if not course_name:
        frappe.throw(_("Course name is required"))
    
    course = frappe.get_doc("Course", course_name)
    
    # Get instructors if any from "Instructor Curso" child table
    instructors = frappe.get_all(
        "Instructor Curso",
        filters={
            "parent": course_name,
            "parentfield": "custom_instructor"
        },
        fields=["instructor", "dni", "horas"],
        ignore_permissions=True
    )
    
    return {
        "name": course.name,
        "course_name": course.course_name,
        "state": course.state,
        "start_date": course.start_date,
        "end_date": course.end_date,
        "hours": course.hours,
        "custom_modalidad": course.custom_modalidad,
        "center": course.center,
        "city": course.city,
        "expediente": course.expediente,
        "code": course.code,
        "custom_horas_practicas": course.custom_horas_practicas,
        "custom_fecha_inicio_practicas": course.custom_fecha_inicio_practicas,
        "custom_fecha_fin_practicas": course.custom_fecha_fin_practicas,
        "custom_fecha_fin_teoria": course.custom_fecha_fin_teoria,
        "instructors": [{"instructor": i.instructor, "dni": i.dni, "horas": i.horas} for i in instructors]
    }
