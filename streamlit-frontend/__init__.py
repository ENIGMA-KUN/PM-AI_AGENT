# Import handler for Windsurf project structure
# This maps kebab-case files to camelCase modules as per windsurf rules

# Import services with correct naming
try:
    # These are now using underscore filenames for Python compatibility
    # but follow camelCase module conventions in the import reference
    from .api_service import ApiService as apiService
    from .task_service import TaskService as taskService
    from .log_service import LogService as logService
except ImportError:
    # Fallback direct imports
    from api_service import ApiService as apiService
    from task_service import TaskService as taskService
    from log_service import LogService as logService
