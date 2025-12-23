
import frappe

def run():
    try:
        if frappe.db.exists("Sidebar Item", "Dashboard Fichaje"):
            doc = frappe.get_doc("Sidebar Item", "Dashboard Fichaje")
            doc.path = "AttendanceAnomalies"
            doc.save()
            frappe.db.commit()
            print("Successfully updated Sidebar Item 'Dashboard Fichaje' path to 'AttendanceAnomalies'")
        else:
            print("Sidebar Item 'Dashboard Fichaje' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
