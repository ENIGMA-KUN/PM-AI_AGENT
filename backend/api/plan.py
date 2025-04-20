from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import os
import sys

# Standard imports
import sys
import os
from typing import List, Dict, Any, Optional

# Important: Following windsurf conventions with module imports
# Add the parent directory to sys.path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import gemini-utils module following windsurf conventions
# File is named gemini-utils.py (kebab-case) but imported as gemini_utils (Python-compatible)
from utils import gemini_utils
# Use the parse_plan_with_gemini function from the module
parse_plan_with_gemini = gemini_utils.parse_plan_with_gemini

# Create router
router = APIRouter(tags=["plan"])

# Models
class PlanInput(BaseModel):
    plan_text: str
    
class StoryItem(BaseModel):
    title: str
    owner: str
    due_date: str
    status: str = "Backlog"
    
class PlanOutput(BaseModel):
    stories: List[StoryItem]
    message: str
    timestamp: str

# Routes
@router.post("/plan", response_model=PlanOutput)
async def create_plan(plan_input: PlanInput):
    """
    Parse the user's plan text and create a structured plan.
    Example: /plan Redesign landing page by Sep-05; Dev: Alice,Bob; Mktg: Carol
    """
    try:
        # Use Gemini for plan parsing
        plan_text = plan_input.plan_text
        
        # Call our Gemini API service to parse the plan text
        parsed_plan = parse_plan_with_gemini(plan_text)
        
        # Extract information from the parsed plan
        title = parsed_plan.get('title', plan_text)
        due_date = parsed_plan.get('due_date', '2025-12-31')
        
        # Extract owners from team members
        owners = []
        for member in parsed_plan.get('team_members', []):
            owners.append(member.get('name', 'Unassigned'))
        
        # Create stories
        stories = [
            StoryItem(
                title=title,
                owner=owner,
                due_date=due_date
            )
            for owner in owners
        ]
        
        # Store the plan in a JSON file
        plan_data = {
            "title": title,
            "due_date": due_date,
            "stories": [story.dict() for story in stories],
            "created_at": datetime.now().isoformat()
        }
        
        os.makedirs("data", exist_ok=True)
        with open("data/plan.json", "w") as f:
            json.dump(plan_data, f, indent=2)
        
        # Update project log
        with open("../project_log.md", "a") as log_file:
            timestamp = datetime.now().strftime("%Y‑%m‑%d %H:%M")
            log_file.write(f"- **{timestamp}**: /plan executed – parsed plan and created {len(stories)} stories\n")
        
        return PlanOutput(
            stories=stories,
            message=f"Plan created with {len(stories)} stories",
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plan: {str(e)}")
