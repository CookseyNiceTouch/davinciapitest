#!/usr/bin/env python3

import sys
import os
import traceback

# Check Python version
print(f"Python version: {sys.version}")
is_64bit = sys.maxsize > 2**32
print(f"Python architecture: {'64-bit' if is_64bit else '32-bit'}")

if not is_64bit:
    print("ERROR: DaVinci Resolve requires 64-bit Python!")
    sys.exit(1)

# Set paths for DaVinci Resolve scripting API
if sys.platform.startswith("win"):
    resolve_script_api = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), 
                                     "Blackmagic Design", "DaVinci Resolve", "Support", 
                                     "Developer", "Scripting")
    resolve_script_lib = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), 
                                     "Blackmagic Design", "DaVinci Resolve", "fusionscript.dll")
elif sys.platform.startswith("darwin"):
    resolve_script_api = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
    resolve_script_lib = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
else:  # Linux
    resolve_script_api = "/opt/resolve/Developer/Scripting"
    resolve_script_lib = "/opt/resolve/libs/Fusion/fusionscript.so"

# Set environment variables
os.environ["RESOLVE_SCRIPT_API"] = resolve_script_api
os.environ["RESOLVE_SCRIPT_LIB"] = resolve_script_lib

# Add API modules path to Python path
modules_path = os.path.join(resolve_script_api, "Modules")
if not os.path.isdir(modules_path):
    print(f"ERROR: Resolve scripting modules path does not exist: {modules_path}")
    print("Please check your DaVinci Resolve installation")
    sys.exit(1)

print(f"Using API modules path: {modules_path}")
sys.path.append(modules_path)

# Attempt to import DaVinciResolveScript
print("Attempting to import DaVinciResolveScript...")
try:
    print("Import starting...")
    import DaVinciResolveScript as dvr_script
    print("Import successful!")
except ImportError as e:
    print(f"ImportError: {e}")
    print(traceback.format_exc())
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error during import: {e}")
    print(traceback.format_exc())
    sys.exit(1)

# Connect to Resolve
print("Connecting to DaVinci Resolve...")
try:
    resolve = dvr_script.scriptapp("Resolve")
    if resolve:
        print("Successfully connected to Resolve!")
    else:
        print("Failed to connect to Resolve. Make sure Resolve is running.")
        sys.exit(1)
except Exception as e:
    print(f"Error connecting to Resolve: {e}")
    print(traceback.format_exc())
    sys.exit(1)

# Get basic information
print("\nBasic Resolve information:")
try:
    version = resolve.GetVersionString()
    print(f"DaVinci Resolve version: {version}")
    
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    
    if current_project:
        project_name = current_project.GetName()
        print(f"Current project: {project_name}")
    else:
        print("No project currently open")
except Exception as e:
    print(f"Error getting Resolve information: {e}")
    print(traceback.format_exc())

print("\nScript completed successfully!")
