
import frappe
from frappe import _
from frappe.utils import now_datetime

@frappe.whitelist()
def sign_document(process_name, row_name):
    """
    Signs the document.
    """
    try:
        # LOGGING INPUTS
        frappe.log_error(f"DEBUG SIGNING: process_name='{process_name}', row_name='{row_name}'", "Signing Debug Input")

        # CHECK EXISTENCE EXPLICITLY
        if not frappe.db.exists("Employee Onboarding Process", process_name):
            frappe.log_error(f"DEBUG SIGNING: Process '{process_name}' NOT FOUND in DB", "Signing Debug Critical")
            # We explicitly throw DoesNotExistError to see if frontend handles it differently
            # But the log is what we need.
            frappe.throw(_("Process detection failed"), exc=frappe.DoesNotExistError)
        else:
             frappe.log_error(f"DEBUG SIGNING: Process '{process_name}' EXISTS", "Signing Debug Critical")

        user = frappe.session.user
        
        # Security: Verify User is Employee
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        frappe.log_error(f"DEBUG SIGNING: User='{user}', Employee='{employee}'", "Signing Debug User")

        if not employee:
            frappe.throw(_("Employee not found for current user"))

        # Security: Verify Onboarding Process Ownership
        process = frappe.get_doc("Employee Onboarding Process", process_name)
        if process.employee != employee:
            frappe.throw(_("Unauthorized access to this onboarding process"))

        # Find the row
        target_row = None
        for row in process.required_documents:
            if row.name == row_name:
                target_row = row
                break
        
        if not target_row:
            frappe.throw(_("Document row not found"))

        if target_row.is_completed:
            frappe.throw(_("Document already signed"))

        # Create Document Acceptance
        # The creation/submit of this doc triggers hooks (after_insert) in document_acceptance.py
        # which automatically update the Onboarding Process status and rows.
        # We do NOT need to save the process manually here, as that causes TimestampMismatchError.
        acceptance = frappe.new_doc("Document Acceptance")
        acceptance.document_reference = target_row.document_reference
        acceptance.employee = employee
        acceptance.onboarding_process = process.name
        acceptance.acceptance_date = now_datetime()
        acceptance.accepted_by_user = user
        acceptance.insert(ignore_permissions=True)
        acceptance.submit()
        
        return {"status": "success", "acceptance": acceptance.name}

    except Exception as e:
        frappe.log_error(f"DEBUG SIGNING EXCEPTION: {str(e)}", "Signing Exception")
        raise e
