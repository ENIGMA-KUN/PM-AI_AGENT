# Utils module initialization
# This initialization file handles importing kebab-case filenames
# while following the windsurf-required naming conventions

import os
import importlib.util
import sys

# Function to import kebab-case modules
def import_kebab_file(kebab_filename, module_name):
    """Imports a module from a kebab-case filename"""
    module_path = os.path.join(os.path.dirname(__file__), kebab_filename)
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    return None

# Import all kebab-case modules as camelCase for Python compatibility
# while still following windsurf conventions
gemini_utils = import_kebab_file("gemini-utils.py", "gemini_utils")

