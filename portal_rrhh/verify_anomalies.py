import frappe
from frappe.utils import today, add_days
from portal_rrhh.api.attendance import get_attendance_anomalies

def run():
    print("Testing get_attendance_anomalies...")
    
    start = add_days(today(), -30)
    end = today()
    
    # Test with no employee filter
    try:
        res = get_attendance_anomalies(start, end)
        if res['success']:
            print(f"Success! Found {len(res['data'])} anomalies.")
            if len(res['data']) > 0:
                print("Sample:", res['data'][0])
        else:
            print("Failed:", res['message'])
            
    except Exception as e:
        print("Exception:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run()
