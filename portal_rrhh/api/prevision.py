import frappe
from frappe import _

@frappe.whitelist()
def get_courses_without_instructor():
    """
    Get courses in Previsto, Planificado or En curso state that don't have an instructor assigned.
    Used for hiring planning/forecasting.
    """
    # Get all courses in Previsto, Planificado or En curso state
    courses = frappe.get_all(
        "Course",
        filters=[["state", "in", ["Previsto", "Planificado", "En curso"]]],
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
    
    # Get unique expediente (Program) names to fetch custom_num_de_expediente
    expediente_names = list(set(c.expediente for c in courses_without_instructor if c.expediente))
    
    # Fetch custom_num_de_expediente for each Program
    expediente_map = {}
    if expediente_names:
        programs = frappe.get_all(
            "Program",
            filters=[["name", "in", expediente_names]],
            fields=["name", "custom_num_de_expediente"],
            ignore_permissions=True
        )
        expediente_map = {p.name: p.custom_num_de_expediente for p in programs}
    
    # Add custom_num_de_expediente to each course
    for course in courses_without_instructor:
        course["expediente_num"] = expediente_map.get(course.expediente) if course.expediente else None
    
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


@frappe.whitelist()
def get_related_instructors(course_name):
    """
    Get employees who have been instructors of the same course or courses in the same professional family.
    Returns two groups: same_course and same_family.
    """
    if not course_name:
        frappe.throw(_("Course name is required"))
    
    course = frappe.get_doc("Course", course_name)
    
    result = {
        "course_name": course.course_name,
        "course_code": course.code,
        "familia_formativa": course.custom_familia_formativa,
        "especialidad": course.custom_especialidad,
        "same_course": [],
        "same_family": []
    }
    
    # Get instructors who have taught THIS EXACT course (by normalized course_name)
    same_course_instructors = get_instructors_for_same_course(course.course_name)
    
    # Get instructors who have taught courses in the same family (excluding same course)
    same_family_instructors = []
    if course.custom_familia_formativa:
        same_family_instructors = get_instructors_for_family(
            course.custom_familia_formativa, 
            course.custom_especialidad,
            exclude_course_name=course.course_name
        )
    
    # Get employee details for same course instructors
    result["same_course"] = enrich_instructors_with_employee_data(same_course_instructors)
    
    # Get employee details for same family instructors (excluding those already in same_course)
    same_course_employees = set(i.get("employee") for i in result["same_course"] if i.get("employee"))
    same_family_filtered = [i for i in same_family_instructors if i.get("employee") not in same_course_employees]
    result["same_family"] = enrich_instructors_with_employee_data(same_family_filtered)
    
    return result


def normalize_course_name(name):
    """Normalize course name for comparison - remove accents, extra spaces, convert to uppercase."""
    if not name:
        return ""
    import unicodedata
    # Remove accents
    normalized = unicodedata.normalize('NFD', name)
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    # Uppercase, strip, remove extra spaces and tabs
    normalized = ' '.join(normalized.upper().split())
    return normalized


def get_instructors_for_same_course(course_name):
    """Get all instructors who have taught courses with the SAME course_name (normalized)."""
    if not course_name:
        return []
    
    # Normalize the target course name
    target_normalized = normalize_course_name(course_name)
    
    if not target_normalized:
        return []
    
    # Get all courses (we need to normalize and compare)
    all_courses = frappe.get_all(
        "Course",
        fields=["name", "course_name"],
        ignore_permissions=True
    )
    
    # Find courses with matching normalized name
    matching_course_names = []
    for c in all_courses:
        if normalize_course_name(c.course_name) == target_normalized:
            matching_course_names.append(c.name)
    
    if not matching_course_names:
        return []
    
    # Get instructors from these courses
    instructor_records = frappe.get_all(
        "Instructor Curso",
        filters=[
            ["parent", "in", matching_course_names],
            ["instructor", "is", "set"]
        ],
        fields=["instructor", "parent"],
        ignore_permissions=True
    )
    
    # Get unique instructors with their course count
    instructor_map = {}
    for rec in instructor_records:
        if rec.instructor not in instructor_map:
            instructor_map[rec.instructor] = {"instructor": rec.instructor, "courses_count": 0, "courses": []}
        instructor_map[rec.instructor]["courses_count"] += 1
        instructor_map[rec.instructor]["courses"].append(rec.parent)
    
    return list(instructor_map.values())


def get_instructors_for_family(familia_formativa, especialidad=None, exclude_course_name=None):
    """Get all instructors who have taught courses in this professional family (excluding the same course)."""
    filters = [["custom_familia_formativa", "=", familia_formativa]]
    
    courses = frappe.get_all(
        "Course",
        filters=filters,
        fields=["name", "code", "course_name", "custom_especialidad"],
        ignore_permissions=True
    )
    
    if not courses:
        return []
    
    # Exclude courses with the same normalized course name
    excluded_normalized = normalize_course_name(exclude_course_name) if exclude_course_name else None
    if excluded_normalized:
        courses = [c for c in courses if normalize_course_name(c.course_name) != excluded_normalized]
    
    if not courses:
        return []
    
    course_names = [c.name for c in courses]
    
    # Get instructors from these courses
    instructor_records = frappe.get_all(
        "Instructor Curso",
        filters=[
            ["parent", "in", course_names],
            ["instructor", "is", "set"]
        ],
        fields=["instructor", "parent"],
        ignore_permissions=True
    )
    
    # Create course lookup for speciality info
    course_lookup = {c.name: c for c in courses}
    
    # Get unique instructors with their course count and specialities
    instructor_map = {}
    for rec in instructor_records:
        if rec.instructor not in instructor_map:
            instructor_map[rec.instructor] = {
                "instructor": rec.instructor, 
                "courses_count": 0, 
                "courses": [],
                "especialidades": set()
            }
        instructor_map[rec.instructor]["courses_count"] += 1
        instructor_map[rec.instructor]["courses"].append(rec.parent)
        course_info = course_lookup.get(rec.parent)
        if course_info and course_info.custom_especialidad:
            instructor_map[rec.instructor]["especialidades"].add(course_info.custom_especialidad)
    
    # Convert sets to lists for JSON serialization
    for inst in instructor_map.values():
        inst["especialidades"] = list(inst["especialidades"])
    
    return list(instructor_map.values())


def enrich_instructors_with_employee_data(instructors):
    """Add employee information to instructor records."""
    if not instructors:
        return []
    
    instructor_names = [i["instructor"] for i in instructors]
    
    # Get instructor records with employee link
    instructor_docs = frappe.get_all(
        "Instructor",
        filters=[["name", "in", instructor_names]],
        fields=["name", "instructor_name", "employee"],
        ignore_permissions=True
    )
    
    instructor_lookup = {i.name: i for i in instructor_docs}
    
    # Get employee IDs
    employee_ids = [i.employee for i in instructor_docs if i.employee]
    
    # Get employee details
    employees = {}
    if employee_ids:
        employee_docs = frappe.get_all(
            "Employee",
            filters=[["name", "in", employee_ids]],
            fields=[
                "name", "employee_name", "first_name", "last_name", "image",
                "cell_number", "personal_email", "company_email", 
                "designation", "department", "status", "custom_municipio"
            ],
            ignore_permissions=True
        )
        employees = {e.name: e for e in employee_docs}
    
    # Enrich instructor data
    result = []
    for inst in instructors:
        instructor_doc = instructor_lookup.get(inst["instructor"], {})
        employee_id = instructor_doc.get("employee") if instructor_doc else None
        employee = employees.get(employee_id, {}) if employee_id else {}
        
        result.append({
            "instructor": inst["instructor"],
            "instructor_name": instructor_doc.get("instructor_name") if instructor_doc else inst["instructor"],
            "employee": employee_id,
            "employee_name": employee.get("employee_name"),
            "image": employee.get("image"),
            "cell_number": employee.get("cell_number"),
            "email": employee.get("personal_email") or employee.get("company_email"),
            "designation": employee.get("designation"),
            "department": employee.get("department"),
            "status": employee.get("status"),
            "municipio": employee.get("custom_municipio"),
            "courses_count": inst.get("courses_count", 0),
            "especialidades": inst.get("especialidades", [])
        })
    
    # Sort by courses_count descending
    result.sort(key=lambda x: x["courses_count"], reverse=True)
    
    return result
