
import frappe

def execute():
    process_name = "ONB-2025-0004"
    if not frappe.db.exists("Employee Onboarding Process", process_name):
        print("Process not found.")
        return

    doc = frappe.get_doc("Employee Onboarding Process", process_name)
    print(f"Fixing process {doc.name}...")
    
    # Existing docs?
    if doc.required_documents:
        print("Process already has documents. Aborting fix to avoid duplicates.")
        return

    # Fetch correct docs
    company = doc.company
    docs = frappe.get_all("Documentos del sistema",
                          filters={
                              "checkbox_onboarding": 1, 
                              "workflow_state": "Vigente"
                          },
                          fields=["name", "title", "document_type"])
    
    valid_docs = []
    print(f"Scanning {len(docs)} system documents for company {company}...")
    
    for d in docs:
        allowed_companies = frappe.get_all("System Document Company", filters={"parent": d.name}, pluck="company")
        
        if not allowed_companies: # Global
             valid_docs.append(d)
        elif company in allowed_companies:
             valid_docs.append(d)
    
    if not valid_docs:
        print("No valid docs found to add.")
        return

    print(f"Adding {len(valid_docs)} documents...")
    for d in valid_docs:
        row = doc.append("required_documents", {})
        row.document_reference = d.name
        row.document_title = d.title
        row.document_type = d.document_type
        row.is_required = 1
        row.is_completed = 0
    
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("SUCCESS: Process updated and saved.")
