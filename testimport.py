import sys
import os

# Explicitly set the path to the DaVinciResolveScript module
resolve_script_module_path = os.path.join(
    "C:\\ProgramData", 
    "Blackmagic Design", 
    "DaVinci Resolve", 
    "Support", 
    "Developer", 
    "Scripting", 
    "Modules", 
    "DaVinciResolveScript.py"
)

# Add the directory containing the module to the Python path
sys.path.append(os.path.dirname(resolve_script_module_path))

try:
    import DaVinciResolveScript as dvr_script
    print("Import successful!")
except Exception as e:
    print(f"Error importing DaVinciResolveScript: {e}")
