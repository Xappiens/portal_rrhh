
import frappe
from portal_rrhh.api.onboarding import create_onboarding_process_if_needed

def execute():
    # 1. Inspect Workflow
    workflows = frappe.get_all("Workflow", filters={"document_type": "Job Offer", "is_active": 1}, fields=["name"])
    if not workflows:
        print("No active workflow for Job Offer.")
        initial_state = "Draft"
    else:
        wf_name = workflows[0].name
        wf_doc = frappe.get_doc("Workflow", wf_name)
        print(f"Active Workflow: {wf_name}")
        states = [s.state for s in wf_doc.states]
        print(f"Valid States: {states}")
        initial_state = states[0] # Assume first state is valid start
    
    # 2. Setup Data
    company_name = "ATU Seguridad y Salud SL" # Known to have no docs
    
    # Create/Get Mock Job Offer
    offer_name = "TEST-OFFER-NO-DOCS"
    if frappe.db.exists("Job Offer", offer_name):
        frappe.delete_doc("Job Offer", offer_name)
    
    # Clean up any potential process
    frappe.db.sql("DELETE FROM `tabEmployee Onboarding Process` WHERE job_offer=%s", offer_name)
    
    offer = frappe.new_doc("Job Offer")
    offer.name = offer_name 
    offer.job_applicant = "Test Applicant"
    offer.applicant_email = "judit.pascual@grupoatu.com" 
    offer.company = company_name
    offer.status = "Accepted"
    offer.workflow_state = initial_state
    
    # Mandatory Fields
    # Check if Designation exists, if not create
    desig_name = "Test Designation"
    if not frappe.db.exists("Designation", desig_name):
         d = frappe.new_doc("Designation")
         d.designation_name = desig_name
         d.insert()
    
    offer.designation = desig_name
    offer.offer_date = "2025-01-01"
    offer.applicant_name = "Test Applicant Name"
    
    # Insert with ignore_permissions and ignore_links if possible, currently ignore_permissions=True
    # If state is invalid, it might crash.
    try:
        offer.insert(ignore_permissions=True)
        print(f"Created Job Offer: {offer.name} in state {offer.workflow_state}")
    except Exception as e:
        print(f"Insert failed: {e}")
        return

    # 3. Simulate Transition to Alta
    # Manually force state to Alta to test the FUNCTION, bypassing workflow rules which might complicate things
    offer.workflow_state = "Alta"
    # DO NOT SAVE. Function uses the doc object passed to it. Saving triggers workflow rules.
    print(f"Forced in-memory state to Alta. Current state: {offer.workflow_state}")

    print("Calling create_onboarding_process_if_needed...")
    create_onboarding_process_if_needed(offer)
    
    # 4. Check Result
    processes = frappe.get_all("Employee Onboarding Process", 
                              filters={"job_offer": offer.name}, 
                              fields=["name", "onboarding_status"])
    
    if processes:
        print(f"FAILURE: Process created! {processes}")
        p = frappe.get_doc("Employee Onboarding Process", processes[0].name)
        print(f"  Docs included: {len(p.required_documents)}")
        
        # Additional debug: why was it created?
        # Check logic in onboarding.py via print statements if needed, or deduce.
    else:
        print("SUCCESS: No process created.")
    
    # Cleanup
    frappe.delete_doc("Job Offer", offer.name)

