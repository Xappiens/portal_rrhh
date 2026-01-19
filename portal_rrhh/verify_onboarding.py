import frappe
from frappe.utils import today

def execute():
    try:
        # 1. Setup Data
        company_name = "ASOCIACIÓN SOCIOCULTURAL DE AVENTURA ATU"
        employee_name_query = "Tania Ordóñez Alonso"
        
        company = frappe.db.get_value("Company", {"name": company_name})
        if not company:
            print(f"ERROR: Company '{company_name}' not found.")
            return

        employee = frappe.db.get_value("Employee", {"employee_name": ["like", f"%{employee_name_query}%"]}, "name")
        if not employee:
            print(f"ERROR: Employee matching '{employee_name_query}' not found.")
            return
        
        print(f"Found Company: {company}")
        print(f"Found Employee: {employee}")

        # 2. Create/Get System Document
        doc_title = "Test Onboarding Doc for Aventura"
        sys_doc = frappe.db.get_value("Documentos del sistema", {"title": doc_title}, "name")
        
        if not sys_doc:
            doc = frappe.new_doc("Documentos del sistema")
            doc.title = doc_title
            doc.document_type = "OnBoarding"
            doc.checkbox_onboarding = 1
            doc.workflow_state = "Borrador" # Initial valid state
            doc.descripcion = "Test doc for Aventura ATU"
            doc.fichero = "<p>This is a test document content.</p>"
            doc.confidentiality_level = "Interno"
            
            # Add Company
            row = doc.append("companies", {})
            row.company = company
            
            doc.insert(ignore_permissions=True)
            
            # FORCE Workflow State Update in DB directly to bypass rules
            doc.db_set("workflow_state", "Vigente")
            
            sys_doc = doc.name
            print(f"Created System Document: {sys_doc} and forced state to Vigente")
        else:
             print(f"Using existing System Document: {sys_doc}")

        # 3. Use Existing Job Offer
        job_offer_name = "HR-OFF-2025-01957"
        job_offer = frappe.get_doc("Job Offer", job_offer_name)
        print(f"Loaded Job Offer: {job_offer.name} in state {job_offer.workflow_state}")

        # 4. Trigger "Alta" via Workflow
        # Workflow: Solicitado -> Tramitar -> Alta
        from frappe.model.workflow import apply_workflow
        
        apply_workflow(job_offer, "Tramitar")
        print(f"Workflow Action 'Tramitar' applied. State: {job_offer.workflow_state}")
        
        frappe.db.commit() 

        # 5. Verify Process Creation
        process = frappe.db.get_value("Employee Onboarding Process", {"job_offer": job_offer.name}, "name")
        if process:
            print(f"SUCCESS: Employee Onboarding Process Created: {process}")
            
            # Verify Document Inclusion
            proc_doc = frappe.get_doc("Employee Onboarding Process", process)
            found_doc = False
            for row in proc_doc.required_documents:
                # We need to find our sys_doc name
                # Since we are using existing doc from previous run, we need to find it again or assume it persists.
                # Let's find the doc we created/found earlier in the script.
                if row.document_reference == sys_doc:
                    found_doc = True
                    break
            
            if found_doc:
                print(f"SUCCESS: Correct document '{sys_doc}' included in process.")
            else:
                 print(f"FAILURE: Document '{sys_doc}' NOT found in process.")
                 print("Documents found in process:", [r.document_reference for r in proc_doc.required_documents])

        else:
            print("FAILURE: Employee Onboarding Process NOT created.")
            
        frappe.db.commit()

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"EXCEPTION: {e}")
        frappe.log_error(f"Verification Failed: {e}")

