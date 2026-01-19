import frappe
from portal_rrhh.api.onboarding import create_onboarding_process_if_needed

def execute():
    job_offer_name = "HR-OFF-2025-01957"
    if not frappe.db.exists("Job Offer", job_offer_name):
        print(f"Job Offer {job_offer_name} not found.")
        return

    doc = frappe.get_doc("Job Offer", job_offer_name)
    doc.workflow_state = "Alta"
    
    print(f"Testing with Job Offer: {job_offer_name}")
    
    # Prerequisite: Cancel ALL existing active processes to simulate "previous cancelled" state
    actives = frappe.get_all("Employee Onboarding Process", 
                             filters={"job_offer": job_offer_name, "docstatus": 0},
                             fields=["name"])
    for a in actives:
        print(f"Cancelling active process {a.name} to prepare test...")
        d = frappe.get_doc("Employee Onboarding Process", a.name)
        d.onboarding_status = "Cancelled" 
        d.flags.ignore_permissions = True
        d.submit()
        d.cancel()
        frappe.db.commit()

    # Check state before
    existing = frappe.get_all("Employee Onboarding Process", 
                              filters={"job_offer": job_offer_name}, 
                              fields=["name", "onboarding_status", "docstatus"],
                              order_by="creation desc")
    print("Existing processes BEFORE (Should be all Cancelled):")
    for e in existing:
        print(f"- {e.name}: Status={e.onboarding_status}, Docstatus={e.docstatus}")

    # Trigger Hook
    print("Triggering create_onboarding_process_if_needed...")
    create_onboarding_process_if_needed(doc, "on_update")
    
    # Check state after
    after = frappe.get_all("Employee Onboarding Process", 
                           filters={"job_offer": job_offer_name}, 
                           fields=["name", "onboarding_status", "docstatus"],
                           order_by="creation desc")
    print("Existing processes AFTER:")
    for e in after:
        print(f"- {e.name}: Status={e.onboarding_status}, Docstatus={e.docstatus}")
        
    # Validation
    # We expect one NEW process (Pending/0) at the top
    if after and after[0].docstatus == 0 and after[0].onboarding_status != "Cancelled":
         if len(after) > len(existing):
             print("SUCCESS: New process created.")
         else:
             # It might be that one created earlier was reused? No, logic is new doc.
             print("FAILURE: Count didn't increase?")
    else:
        print("FAILURE: Top process is not new/active.")

execute()
