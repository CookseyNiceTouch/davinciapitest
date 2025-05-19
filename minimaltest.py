import sys
import os
# Minimal setup from your script for paths
resolve_script_api = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), 
                                 "Blackmagic Design", "DaVinci Resolve", "Support", 
                                 "Developer", "Scripting")
modules_path = os.path.join(resolve_script_api, "Modules")
if modules_path not in sys.path:
    sys.path.append(modules_path)

print(f"Python version: {sys.version}")
print(f"sys.path includes: {modules_path in sys.path}")
print(f"Modules path exists: {os.path.isdir(modules_path)}")

try:
    print("Attempting minimal import...")
    import DaVinciResolveScript
    print("Minimal import successful.")
except Exception as e:
    print(f"Error during minimal import: {e}")
    import traceback
    print(traceback.format_exc())
