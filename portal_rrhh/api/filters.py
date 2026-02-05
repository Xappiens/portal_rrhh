import frappe
from frappe import _

@frappe.whitelist()
def get_unique_provinces():
    """Get list of unique provinces from Job Offers"""
    try:
        JobOffer = frappe.qb.DocType("Job Offer")
        
        query = (
            frappe.qb.from_(JobOffer)
            .select(JobOffer.custom_provincia)
            .where(JobOffer.custom_provincia.isnotnull())
            .where(JobOffer.custom_provincia != "")
            .distinct()
            .orderby(JobOffer.custom_provincia)
        )
        
        provinces = query.run(as_dict=True)
        result = [p['custom_provincia'] for p in provinces if p.get('custom_provincia')]
        return result
    except Exception as e:
        # Log solo el tipo de error, no el mensaje completo para evitar problemas de longitud
        error_msg = str(e)[:100] if len(str(e)) > 100 else str(e)
        frappe.log_error(f"Error get_unique_provinces: {error_msg}", "Filters API Error")
        return []

@frappe.whitelist()
def get_unique_companies():
    """Get list of unique companies from Job Offers"""
    try:
        JobOffer = frappe.qb.DocType("Job Offer")
        
        query = (
            frappe.qb.from_(JobOffer)
            .select(JobOffer.company)
            .where(JobOffer.company.isnotnull())
            .where(JobOffer.company != "")
            .distinct()
            .orderby(JobOffer.company)
        )
        
        companies = query.run(as_dict=True)
        return [c['company'] for c in companies if c.get('company')]
    except Exception as e:
        # Log solo el tipo de error, no el mensaje completo para evitar problemas de longitud
        error_msg = str(e)[:100] if len(str(e)) > 100 else str(e)
        frappe.log_error(f"Error get_unique_companies: {error_msg}", "Filters API Error")
        return []


@frappe.whitelist()
def get_unique_reports_to():
    """Get list of unique managers (reports_to) from Employees"""
    try:
        Employee = frappe.qb.DocType("Employee")
        Manager = frappe.qb.DocType("Employee").as_("manager")
        
        # Get distinct reports_to values with employee names
        query = (
            frappe.qb.from_(Employee)
            .join(Manager)
            .on(Employee.reports_to == Manager.name)
            .select(
                Employee.reports_to,
                Manager.employee_name
            )
            .where(Employee.reports_to.isnotnull())
            .where(Employee.reports_to != "")
            .where(Employee.status == "Active")
            .distinct()
            .orderby(Manager.employee_name)
        )
        
        managers = query.run(as_dict=True)
        # Return list of objects with value and label
        result = []
        seen = set()
        for m in managers:
            if m.get('reports_to') and m['reports_to'] not in seen:
                seen.add(m['reports_to'])
                result.append({
                    'value': m['reports_to'],
                    'label': m.get('employee_name') or m['reports_to']
                })
        return result
    except Exception as e:
        error_msg = str(e)[:100] if len(str(e)) > 100 else str(e)
        frappe.log_error(f"Error get_unique_reports_to: {error_msg}", "Filters API Error")
        return []
