import frappe
from portal_rrhh.portal_rrhh.api.timesheets import get_planes

def execute():
    try:
        # Test with the problematic query
        results = get_planes(txt="fortra")
        print(f"Query 'fortra' returned {len(results)} results")
        for r in results:
            print(f"Result: {r}")
            
        # Also test with exact match from DB just in case
        results_exact = get_planes(txt="FORTRA")
        print(f"Query 'FORTRA' returned {len(results_exact)} results")
        
    except Exception as e:
        print(f"Error: {e}")
