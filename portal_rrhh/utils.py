import frappe
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect

def before_request():
	if frappe.request.path.startswith("/hrms") or frappe.request.path == "/hrms":
		raise HTTPException(response=redirect("/portal-rrhh/dashboard"))
