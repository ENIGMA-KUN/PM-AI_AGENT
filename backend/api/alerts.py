from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Models
class AlertTask(BaseModel):
    id: str
    title: str
    owner: str
    due_date: datetime
    days_overdue: int

class AlertResponse(BaseModel):
    message: str
    alerts_sent: int
    overdue_tasks: List[AlertTask]

class AlertRequest(BaseModel):
    send_notifications: bool = True
    include_pending: bool = False

# Helper functions
def load_plan_data():
    """Load the current plan data to check for overdue tasks."""
    try:
        plan_path = os.path.join("data", "plan.json")
        if not os.path.exists(plan_path):
            logger.warning("No plan.json found. Creating empty plan.")
            return {"tasks": []}
        
        with open(plan_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading plan data: {e}")
        return {"tasks": []}

def find_overdue_tasks(include_pending=False):
    """Find tasks that are overdue based on their due date."""
    plan_data = load_plan_data()
    today = datetime.now().date()
    overdue_tasks = []
    
    for task in plan_data.get("tasks", []):
        # Skip if task has no due date or is already done
        if not task.get("due_date") or (task.get("status", "").lower() == "done" and not include_pending):
            continue
        
        due_date = datetime.fromisoformat(task["due_date"]).date()
        if due_date < today:
            days_overdue = (today - due_date).days
            overdue_tasks.append(
                AlertTask(
                    id=task.get("id", "unknown"),
                    title=task.get("title", "Untitled Task"),
                    owner=task.get("owner", "Unassigned"),
                    due_date=datetime.fromisoformat(task["due_date"]),
                    days_overdue=days_overdue
                )
            )
    
    return overdue_tasks

def send_notifications(overdue_tasks: List[AlertTask]):
    """Send notifications to task owners about overdue tasks."""
    notifications_sent = 0
    for task in overdue_tasks:
        try:
            # In a real system, this would call notification service (email, Slack, etc.)
            logger.info(f"Sending notification to {task.owner} about task '{task.title}' overdue by {task.days_overdue} days")
            
            # Log to project_log.md
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            log_entry = f"- **{timestamp}**: Alert sent to {task.owner} for overdue task '{task.title}' ({task.days_overdue} days late)"
            append_to_project_log(log_entry)
            
            notifications_sent += 1
        except Exception as e:
            logger.error(f"Failed to send notification for task {task.id}: {e}")
    
    return notifications_sent

def append_to_project_log(log_entry):
    """Append an entry to the project_log.md file."""
    try:
        log_path = os.path.join("..", "project_log.md")
        
        # Read existing content
        with open(log_path, "r") as f:
            content = f.read()
        
        # Append new entry
        with open(log_path, "w") as f:
            f.write(content + "\n" + log_entry)
            
        logger.info("Added entry to project_log.md")
    except Exception as e:
        logger.error(f"Failed to update project log: {e}")

# Routes
@router.post("/alerts", response_model=AlertResponse)
async def check_overdue_tasks(request: AlertRequest, background_tasks: BackgroundTasks):
    """
    Check for overdue tasks and optionally send notifications to owners.
    
    - `send_notifications`: If true, will send notifications to task owners
    - `include_pending`: If true, will include tasks marked as Done
    """
    overdue_tasks = find_overdue_tasks(include_pending=request.include_pending)
    
    if not overdue_tasks:
        return AlertResponse(
            message="No overdue tasks found.",
            alerts_sent=0,
            overdue_tasks=[]
        )
    
    notifications_sent = 0
    if request.send_notifications:
        notifications_sent = send_notifications(overdue_tasks)
    
    return AlertResponse(
        message=f"Found {len(overdue_tasks)} overdue tasks. Sent {notifications_sent} notifications.",
        alerts_sent=notifications_sent,
        overdue_tasks=overdue_tasks
    )

@router.get("/alerts/check", response_model=AlertResponse)
async def check_alerts():
    """Quick check endpoint that just reports overdue tasks without sending notifications."""
    overdue_tasks = find_overdue_tasks()
    
    return AlertResponse(
        message=f"Found {len(overdue_tasks)} overdue tasks.",
        alerts_sent=0,
        overdue_tasks=overdue_tasks
    )
