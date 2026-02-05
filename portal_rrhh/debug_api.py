import frappe
import importlib

def run():
    print("DEBUG: Starting verification of API method...")
    method_path = "portal_rrhh.api.onboarding.sign_onboarding_document"
    
    try:
        # Try importing the module first
        print(f"DEBUG: Attempting to import module portal_rrhh.api.onboarding")
        import portal_rrhh
        print(f"DEBUG: portal_rrhh package file: {getattr(portal_rrhh, '__file__', 'UNKNOWN')}")
        import portal_rrhh.api.onboarding
        module = portal_rrhh.api.onboarding
        print(f"DEBUG: Module imported successfully: {module}")
        print(f"DEBUG: Module file location: {getattr(module, '__file__', 'UNKNOWN')}")
        
        # Check for function
        if hasattr(module, "sign_onboarding_document"):
            print("DEBUG: Function 'sign_onboarding_document' FOUND in module.")
            func = getattr(module, "sign_onboarding_document")
            print(f"DEBUG: Function object: {func}")
            
            # Check for whitelist check (optional but good to know)
            if hasattr(func, "whitelisted"):
                 print(f"DEBUG: Function is Whitelisted: {func.whitelisted}")
            else:
                 # In some versions it's in frappe.whitelisted
                 print("DEBUG: Function whitelisted attribute not found on function obj (might be stored elsewhere).")

        # Check ping
        if hasattr(module, "ping"):
             ping_func = getattr(module, "ping")
             print(f"DEBUG: Ping function found. Whitelisted attr: {getattr(ping_func, 'whitelisted', 'MISSING')}")

        else:
            print("DEBUG: Function 'sign_onboarding_document' NOT FOUND in module.")
            print("DEBUG: Dir of module:", dir(module))

        # Try frappe.get_attr
        print(f"DEBUG: Attempting frappe.get_attr('{method_path}')")
        method = frappe.get_attr(method_path)
        print(f"DEBUG: frappe.get_attr SUCCESS: {method}")

    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        import traceback
        traceback.print_exc()

