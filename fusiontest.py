import sys
import os

def load_dynamic(module_name, file_path):
    print(f"Attempting to load module: {module_name} from {file_path}")
    import importlib.machinery
    import importlib.util

    loader = importlib.machinery.ExtensionFileLoader(module_name, file_path)
    spec = importlib.util.spec_from_loader(module_name, loader)
    if spec is None:
        print("Failed to create a spec for the module.")
        return None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

try:
    script_module = load_dynamic("fusionscript", "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\fusionscript.dll")  # Adjust for your OS
    if script_module:
        print("fusionscript loaded successfully!")
    else:
        print("Failed to load fusionscript.")
except ImportError as e:
    print(f"Error loading fusionscript: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
