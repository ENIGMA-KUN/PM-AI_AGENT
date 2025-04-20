from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import os

# Create router
router = APIRouter(tags=["risk"])

# Models
class RiskItem(BaseModel):
    story_id: str
    title: str
    on_track: bool
    reason: Optional[str] = None
    
class RiskCheckInput(BaseModel):
    team_lead: str
    items: List[RiskItem]
    
class RiskCheckOutput(BaseModel):
    message: str
    blockers: List[RiskItem]
    needs_discussion: List[RiskItem]
    timestamp: str

# Routes
@router.post("/risk", response_model=RiskCheckOutput)
async def check_risk(risk_input: RiskCheckInput):
    """
    Process risk check-in from team leads.
    Identifies blockers and items that need discussion.
    """
    try:
        # Identify blockers and discussion items
        blockers = []
        needs_discussion = []
        
        for item in risk_input.items:
            if not item.on_track:
                blockers.append(item)
                
                # Check if item needs discussion
                if item.reason and any(reason in item.reason.lower() for reason in ["need discussion", "missing estimated completion"]):
                    needs_discussion.append(item)
        
        # Log the risk check results
        os.makedirs("data", exist_ok=True)
        risk_data = {
            "team_lead": risk_input.team_lead,
            "blockers": [blocker.dict() for blocker in blockers],
            "needs_discussion": [item.dict() for item in needs_discussion],
            "timestamp": datetime.now().isoformat()
        }
        
        # Save risk check data
        with open(f"data/risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(risk_data, f, indent=2)
        
        # Update project log
        with open("../project_log.md", "a") as log_file:
            timestamp = datetime.now().strftime("%Y‑%m‑%d %H:%M")
            log_entry = f"- **{timestamp}**: /risk – {risk_input.team_lead} reported "
            
            if blockers:
                log_entry += f"{len(blockers)} blocker(s)"
                
                if needs_discussion:
                    log_entry += f" and {len(needs_discussion)} item(s) needing discussion"
            elif needs_discussion:
                log_entry += f"{len(needs_discussion)} item(s) needing discussion"
            else:
                log_entry += "no blockers"
                
            log_file.write(log_entry + "\n")
        
        # Create notification content for PM
        notification = f"🚨 Risk check-in from {risk_input.team_lead}:"
        if blockers:
            notification += f" {len(blockers)} blocker(s) reported."
        
        # Here we would typically send an email notification
        # For now, we'll just log it
        print(notification)
        
        return RiskCheckOutput(
            message=f"Risk check-in processed for {risk_input.team_lead}",
            blockers=blockers,
            needs_discussion=needs_discussion,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process risk check-in: {str(e)}")

# Route to get active stories for a team lead
@router.get("/risk/stories/{team_lead}")
async def get_stories_for_lead(team_lead: str):
    """
    Get the list of active stories for a team lead.
    In a real implementation, this would query a database.
    """
    try:
        # For demo purposes, return mock data
        # In a real implementation, we would query the database
        mock_stories = [
            {
                "story_id": "S-001",
                "title": "Redesign landing page",
                "owner": team_lead,
                "due_date": "2025-09-05",
                "status": "In Progress"
            },
            {
                "story_id": "S-002",
                "title": "Implement login flow",
                "owner": team_lead,
                "due_date": "2025-08-15",
                "status": "In Progress"
            }
        ]
        
        return {
            "team_lead": team_lead,
            "stories": mock_stories
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stories: {str(e)}")
