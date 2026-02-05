
import frappe

def execute():
    user_id = 'judit.pascual@grupoatu.com'
    employee = frappe.db.get_value('Employee', {'user_id': user_id}, 'name')
    print(f'Employee: {employee}')
    if employee:
        onboardings = frappe.get_all('Employee Onboarding Process', filters={'employee': employee}, fields=['name', 'docstatus', 'onboarding_status'])
        print(f'Onboardings: {onboardings}')
        
        # Check Job Offer related to this employee if possible, or search for Job Offer by user_id if that link exists
        # Actually simplest is just to check Onboarding docs.
        
        # Let's also check if there are any "Pending" or "Open" onboardings that might be "Active"
        for onb in onboardings:
             doc = frappe.get_doc("Employee Onboarding Process", onb.name)
             print(f"Onboarding {onb.name}: docstatus={doc.docstatus}, onboarding_status={doc.onboarding_status}")
             print(f"  Created: {doc.creation} by {doc.owner}")
             print(f"  Company: {doc.company}")
             print(f"  Job Offer: {doc.job_offer}")

             # Check required_documents
             if not doc.required_documents:
                 print("  WARNING: No required documents found in child table.")
             
             for row in doc.required_documents:
                 print(f"  Doc: {row.document_title} ({row.document_reference}), required={row.is_required}, completed={row.is_completed}")
             
             # Calculate expected docs
             docs = frappe.get_all("Documentos del sistema",
                          filters={
                              "checkbox_onboarding": 1, 
                              "workflow_state": "Vigente"
                          },
                          fields=["name", "title", "document_type"])
             
             print(f"  -- Simulating Document Discovery for company '{doc.company}' --")
             valid_docs = []
             for d in docs:
                allowed = frappe.get_all("System Document Company", filters={"parent": d.name}, pluck="company")
                if not allowed:
                    print(f"    Found Global Doc: {d.title}")
                    valid_docs.append(d)
                elif doc.company and doc.company in allowed:
                    print(f"    Found Company Specific Doc: {d.title}")
                    valid_docs.append(d)
                else:
                    print(f"    Skipping Doc (other companies): {d.title} (Allowed: {allowed})")
             
             if not valid_docs:
                 print("  WARNING: No VALID documents found for this company currently.")



