import requests
import json
from typing import Dict, List, Any, Optional
import os
import sys
from datetime import datetime

# Constants
API_BASE_URL = "http://localhost:8000/api"
BACKEND_URL = "http://localhost:8000"

class ApiService:
    """Service for communicating with the backend API"""
    
    # Make constants available as class attributes
    API_BASE_URL = API_BASE_URL
    BACKEND_URL = BACKEND_URL
    HEADERS = {"Content-Type": "application/json"}
    
    @staticmethod
    def check_health() -> tuple:
        """Check if the backend API is reachable and healthy"""
        try:
            response = requests.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                return True, response.json()
            return False, None
        except Exception as e:
            return False, str(e)
    
    @classmethod
    def create_plan(cls, project_name, description, start_date, end_date, team_members=None):
        """Create a project plan"""
        try:
            # Ensure team_members is a list and format properly
            if not team_members:
                team_members = ["PM", "Dev: Alice", "Dev: Bob"]
                
            team_str = f"; Team: {','.join(team_members)}"
            
            # Format the plan_text according to the windsurf format requirements
            # Format: /plan {name} by {date}; Team: {team}; {description}
            plan_text = f"/plan {project_name} by {end_date.split('T')[0]}{team_str}; {description}"
            
            # Log the request for debugging
            print(f"Sending plan request: {plan_text}")
            
            # Send the request to the backend
            response = requests.post(
                f"{cls.API_BASE_URL}/plan",
                json={"plan_text": plan_text},
                headers=cls.HEADERS
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Update the task.json file with the new plan
            cls._update_task_json(project_name, description, team_members, result)
            
            # Log the action in project_log.md
            cls._append_to_project_log(f"/plan – {project_name} created with {len(team_members)} team members")
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"Error creating plan: {str(e)}")
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_json = e.response.json()
                    if 'detail' in error_json:
                        error_msg = error_json['detail']
                except:
                    pass
            return {"error": error_msg}
    
    @classmethod
    def _update_task_json(cls, project_name, description, team_members, plan_result):
        """Update task.json with the new plan according to windsurf requirements"""
        try:
            import json
            import os
            
            # Path to task.json in the project root
            task_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "task.json")
            
            # Load existing tasks if available
            tasks = []
            if os.path.exists(task_json_path):
                with open(task_json_path, 'r') as f:
                    tasks = json.load(f)
            
            # Get the next task ID
            next_id = 1
            if tasks:
                # Extract numbers from existing task IDs and find the maximum
                existing_ids = [int(task["Task ID"].split('-')[1]) for task in tasks if "Task ID" in task and task["Task ID"].startswith("TSK-")]
                if existing_ids:
                    next_id = max(existing_ids) + 1
            
            # Create a new task for the plan
            new_task = {
                "Task ID": f"TSK-{next_id:03d}",
                "Title": f"Plan: {project_name}",
                "Status": "InProgress",
                "Dependencies": "",
                "Priority": "High",
                "Description": description,
                "Details": f"Team: {','.join(team_members)}; Created via /plan command",
                "Test Strategy": "Validate all stories are created and accessible in Kanban board"
            }
            
            # Add the new task
            tasks.append(new_task)
            
            # Save the updated task.json
            with open(task_json_path, 'w') as f:
                json.dump(tasks, f, indent=2)
            
            print(f"Updated task.json with new plan task: {new_task['Task ID']}")
            return True
        except Exception as e:
            print(f"Error updating task.json: {str(e)}")
            return False
    
    @classmethod
    def _append_to_project_log(cls, message):
        """Append a message to project_log.md with timestamp according to windsurf rules"""
        try:
            import os
            from datetime import datetime
            
            # Path to project_log.md in the project root
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project_log.md")
            
            # Create the file if it doesn't exist
            if not os.path.exists(log_path):
                with open(log_path, 'w') as f:
                    f.write("# Project Log\n\n")
            
            # Format timestamp according to windsurf format (YYYY‑MM‑DD HH:MM)
            timestamp = datetime.now().strftime("%Y‑%m‑%d %H:%M")
            
            # Append the log entry
            with open(log_path, 'a') as f:
                f.write(f"- **{timestamp}**: {message}\n")
            
            print(f"Added entry to project_log.md: {message}")
            return True
        except Exception as e:
            print(f"Error updating project_log.md: {str(e)}")
            return False
    
    @staticmethod
    def send_risk_checkin(task_id: str, recipients: List[str], message: str) -> Dict:
        """Send risk check-in to team leads"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/risk",
                json={
                    "task_id": task_id,
                    "recipients": recipients,
                    "message": message,
                    "team_lead": recipients[0] if recipients else ""  # Added required team_lead field
                }
            )
            
            if response.status_code != 200:
                error_msg = f"API error: {response.text}"
                print(f"Error response: {response.text}")
                return {"error": error_msg}
                
            return response.json()
        except Exception as e:
            print(f"Exception: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def check_alerts(include_pending: bool = False, send_notifications: bool = True) -> Dict:
        """Check for overdue tasks and optionally send notifications"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/alerts",
                json={
                    "include_pending": include_pending,
                    "send_notifications": send_notifications
                }
            )
            
            if response.status_code != 200:
                error_msg = f"API error: {response.text}"
                print(f"Error response: {response.text}")
                return {"error": error_msg}
                
            return response.json()
        except Exception as e:
            print(f"Exception: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def generate_digest(report_name: str, recipients: List[str], include_metrics: bool = True, include_risks: bool = True) -> Dict:
        """Generate a project status report"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/digest",
                json={
                    "title": report_name,  # Changed from report_name to title
                    "recipients": recipients,
                    "include_metrics": include_metrics,
                    "include_risks": include_risks,
                    "format": "pdf"  # Added required format field
                }
            )
            
            if response.status_code != 200:
                error_msg = f"API error: {response.text}"
                print(f"Error response: {response.text}")
                return {"error": error_msg}
                
            return response.json()
        except Exception as e:
            print(f"Exception: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def schedule_meeting(title: str, datetime_str: str, duration_minutes: int, attendees: List[str]) -> Dict:
        """Schedule a triage meeting"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/schedule",
                json={
                    "title": title,
                    "datetime": datetime_str,
                    "duration_minutes": duration_minutes,
                    "attendees": attendees,
                    "location": "Virtual Meeting"  # Added required location field
                }
            )
            
            if response.status_code != 200:
                error_msg = f"API error: {response.text}"
                print(f"Error response: {response.text}")
                return {"error": error_msg}
                
            return response.json()
        except Exception as e:
            print(f"Exception: {str(e)}")
            return {"error": str(e)}
