import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class TaskService:
    """Service for handling task.json and project data"""
    
    @staticmethod
    def load_tasks() -> List[Dict]:
        """Load tasks from task.json"""
        try:
            task_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "task.json")
            with open(task_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading tasks: {e}")
            return []
    
    @staticmethod
    def save_tasks(tasks: List[Dict]) -> bool:
        """Save tasks to task.json"""
        try:
            task_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "task.json")
            with open(task_path, "w") as f:
                json.dump(tasks, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            return False
    
    @staticmethod
    def add_task(task_data: Dict) -> str:
        """Add a new task to task.json"""
        tasks = TaskService.load_tasks()
        
        # Generate task ID
        last_id = 0
        for task in tasks:
            if task.get("Task ID", "").startswith("TSK-"):
                try:
                    task_num = int(task.get("Task ID", "TSK-0").split("-")[1])
                    if task_num > last_id:
                        last_id = task_num
                except ValueError:
                    pass
        
        new_id = f"TSK-{str(last_id + 1).zfill(3)}"
        
        # Create new task
        new_task = {
            "Task ID": new_id,
            "Title": task_data.get("Title", "Untitled Task"),
            "Status": task_data.get("Status", "Todo"),
            "Dependencies": task_data.get("Dependencies", ""),
            "Priority": task_data.get("Priority", "Medium"),
            "Description": task_data.get("Description", ""),
            "Details": task_data.get("Details", ""),
            "Test Strategy": task_data.get("Test Strategy", "")
        }
        
        tasks.append(new_task)
        
        # Save updated tasks
        if TaskService.save_tasks(tasks):
            return new_id
        return ""
    
    @staticmethod
    def update_task_status(task_id: str, new_status: str) -> bool:
        """Update the status of a task"""
        tasks = TaskService.load_tasks()
        
        for task in tasks:
            if task.get("Task ID") == task_id:
                task["Status"] = new_status
                return TaskService.save_tasks(tasks)
        
        return False
    
    @staticmethod
    def get_task_by_id(task_id: str) -> Optional[Dict]:
        """Get a task by its ID"""
        tasks = TaskService.load_tasks()
        
        for task in tasks:
            if task.get("Task ID") == task_id:
                return task
        
        return None
    
    @staticmethod
    def log_task_action(task_id: str, action: str) -> bool:
        """Log a task action to project_log.md"""
        try:
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project_log.md")
            
            # Read existing content
            with open(log_path, "r") as f:
                content = f.read()
            
            # Append new entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(log_path, "w") as f:
                f.write(content + f"\n- **{timestamp}**: {action} for task {task_id}")
                
            return True
        except Exception as e:
            print(f"Failed to update project log: {e}")
            return False
