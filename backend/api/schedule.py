from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
import logging
import random
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Models
class Attendee(BaseModel):
    name: str
    email: str

class MeetingRequest(BaseModel):
    title: str = "Project Triage Meeting"
    duration_minutes: int = 15
    auto_schedule: bool = True
    blocked_stories: Optional[List[str]] = None
    additional_attendees: Optional[List[Attendee]] = None
    preferred_start_time: Optional[str] = None  # format: HH:MM (24-hour)
    preferred_day: Optional[str] = None  # format: YYYY-MM-DD

class MeetingResponse(BaseModel):
    message: str
    meeting_id: Optional[str] = None
    scheduled_time: Optional[str] = None
    meeting_link: Optional[str] = None
    attendees: Optional[List[str]] = None

# Helper functions
def load_plan_data():
    """Load the current plan data to find blocked stories."""
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

def get_blocked_stories():
    """Find stories that are currently blocked."""
    plan_data = load_plan_data()
    blocked_stories = []
    
    for task in plan_data.get("tasks", []):
        if task.get("status") == "Blocked" or task.get("has_blockers", False):
            blocked_stories.append({
                "id": task.get("id", "unknown"),
                "title": task.get("title", "Untitled Task"),
                "owner": task.get("owner", "Unassigned"),
                "blocker_description": task.get("blocker_description", "Unknown blocker")
            })
    
    return blocked_stories

def get_team_leads():
    """Get list of team leads from the system."""
    # In a real system, this would query a database
    # For demo purposes, we'll return a hardcoded list
    return [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"},
        {"name": "Carol", "email": "carol@example.com"}
    ]

def find_next_available_slot(duration_minutes=15, preferred_start_time=None, preferred_day=None):
    """
    Find the next available time slot on the calendar.
    
    In a real system, this would use the Google Calendar API to check free/busy status.
    For demo purposes, we'll simulate finding a slot.
    """
    # Default to today if no preferred day
    if preferred_day:
        try:
            start_date = datetime.strptime(preferred_day, "%Y-%m-%d").date()
        except ValueError:
            start_date = datetime.now().date()
    else:
        start_date = datetime.now().date()
    
    # Default to 10:00 AM if no preferred time
    if preferred_start_time:
        try:
            preferred_hour, preferred_minute = map(int, preferred_start_time.split(":"))
            if 0 <= preferred_hour < 24 and 0 <= preferred_minute < 60:
                start_time = datetime.combine(start_date, datetime.min.time().replace(hour=preferred_hour, minute=preferred_minute))
            else:
                start_time = datetime.combine(start_date, datetime.min.time().replace(hour=10, minute=0))
        except (ValueError, TypeError):
            start_time = datetime.combine(start_date, datetime.min.time().replace(hour=10, minute=0))
    else:
        start_time = datetime.combine(start_date, datetime.min.time().replace(hour=10, minute=0))
    
    # Make sure we're not scheduling in the past
    now = datetime.now()
    if start_time < now:
        # If the preferred time is in the past today, move to tomorrow
        if start_time.date() == now.date():
            start_time = datetime.combine(now.date() + timedelta(days=1), start_time.time())
        # If we're still in the past, use now + 1 hour rounded to nearest 15 min
        if start_time < now:
            start_time = now + timedelta(hours=1)
            start_time = start_time.replace(minute=(start_time.minute // 15) * 15, second=0, microsecond=0)
    
    # Simulate checking calendar availability
    # For demo purposes, we'll just add a small random offset (0-2 hours)
    random_offset = timedelta(minutes=random.randint(0, 120))
    start_time += random_offset
    
    # Round to nearest 15 minutes
    start_time = start_time.replace(minute=(start_time.minute // 15) * 15, second=0, microsecond=0)
    
    # Calculate end time
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    return {
        "start_time": start_time,
        "end_time": end_time
    }

def create_calendar_event(title, start_time, end_time, attendees, description):
    """
    Create a calendar event using Google Calendar API.
    
    For demo purposes, we'll simulate creating an event and return a mock response.
    """
    # In a real application, this would use the Google Calendar API
    # Here we'll just create a mock event ID and meeting link
    event_id = f"event_{int(datetime.now().timestamp())}"
    meeting_link = f"https://meet.google.com/{event_id[:4]}-{event_id[4:8]}-{event_id[8:12]}"
    
    # Log the action
    logger.info(f"Created meeting: {title} at {start_time.isoformat()}")
    logger.info(f"Attendees: {', '.join([a['email'] for a in attendees])}")
    
    # In a real app, we would use the Google Calendar API like this:
    """
    credentials = Credentials.from_authorized_user_info(info=token_info)
    service = build("calendar", "v3", credentials=credentials)
    
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
        'attendees': [{'email': attendee['email']} for attendee in attendees],
        'conferenceData': {
            'createRequest': {
                'requestId': f"meeting-{int(datetime.now().timestamp())}",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        },
    }
    
    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()
    
    event_id = event['id']
    meeting_link = event.get('hangoutLink', 'No video conference link available')
    """
    
    return {
        "event_id": event_id,
        "meeting_link": meeting_link
    }

def send_meeting_invitations(title, start_time, end_time, attendees, meeting_link, description):
    """
    Send email invitations to meeting attendees.
    
    For demo purposes, we'll simulate sending emails.
    """
    # In a real application, this would use Gmail API or another email service
    for attendee in attendees:
        logger.info(f"Sending meeting invitation to {attendee['email']}")
    
    # In a real app, we would use the Gmail API like this:
    """
    credentials = Credentials.from_authorized_user_info(info=token_info)
    service = build('gmail', 'v1', credentials=credentials)
    
    for attendee in attendees:
        message_text = f'''
        Hello {attendee['name']},
        
        You are invited to a project triage meeting.
        
        Title: {title}
        Time: {start_time.strftime('%A, %B %d, %Y at %I:%M %p')}
        Duration: {(end_time - start_time).total_seconds() / 60} minutes
        
        Meeting link: {meeting_link}
        
        Description:
        {description}
        
        Please let me know if you cannot attend.
        
        Thank you,
        PM Agent
        '''
        
        message = MIMEText(message_text)
        message['to'] = attendee['email']
        message['subject'] = f"Invitation: {title}"
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        try:
            message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
        except Exception as e:
            logger.error(f"Error sending email to {attendee['email']}: {e}")
    """
    
    return True

def append_to_project_log(log_entry):
    """Append a new entry to the project_log.md file."""
    try:
        log_path = os.path.join("..", "project_log.md")
        
        # Read existing content
        with open(log_path, "r") as f:
            content = f.read()
        
        # Format the timestamp with Unicode hyphens to match style
        timestamp = datetime.now().strftime('%Y\u2011%m\u2011%d %H:%M')
        
        # Append new entry
        with open(log_path, "w") as f:
            f.write(f"{content}\n- **{timestamp}**: {log_entry}")
            
        logger.info(f"Added entry to project_log.md: {log_entry}")
    except Exception as e:
        logger.error(f"Failed to update project log: {e}")

# Routes
@router.post("/schedule", response_model=MeetingResponse)
async def schedule_meeting(request: MeetingRequest):
    """
    Schedule a triage meeting for blocked stories.
    
    - Automatically finds blocked stories if none specified
    - Schedules with team leads and relevant stakeholders
    - Creates a Google Calendar event with video link
    - Sends email invitations to attendees
    """
    try:
        # Get blocked stories
        blocked = []
        if request.blocked_stories:
            blocked = request.blocked_stories
        else:
            blocked_stories = get_blocked_stories()
            blocked = [f"{story['id']}: {story['title']}" for story in blocked_stories]
        
        # Create meeting title
        title = request.title
        if not title or title == "Project Triage Meeting":
            title = f"Project Triage Meeting - {datetime.now().strftime('%Y-%m-%d')}"
            if len(blocked) > 0:
                title = f"Triage Meeting - {len(blocked)} Blocked Stories"
        
        # Get attendees - team leads for blocked stories + additional attendees
        attendees = get_team_leads()
        if request.additional_attendees:
            for attendee in request.additional_attendees:
                if attendee.email not in [a["email"] for a in attendees]:
                    attendees.append({"name": attendee.name, "email": attendee.email})
        
        # Find available time slot
        slot = find_next_available_slot(
            duration_minutes=request.duration_minutes,
            preferred_start_time=request.preferred_start_time,
            preferred_day=request.preferred_day
        )
        
        # Create description with blocked stories
        description = "Triage meeting to discuss blocked stories:\n\n"
        for i, story in enumerate(blocked, 1):
            description += f"{i}. {story}\n"
        
        # Create calendar event
        if request.auto_schedule:
            event = create_calendar_event(
                title=title,
                start_time=slot["start_time"],
                end_time=slot["end_time"],
                attendees=attendees,
                description=description
            )
            
            # Send meeting invitations
            send_meeting_invitations(
                title=title,
                start_time=slot["start_time"],
                end_time=slot["end_time"],
                attendees=attendees,
                meeting_link=event["meeting_link"],
                description=description
            )
            
            # Log the action
            attendee_list = ", ".join([a["name"] for a in attendees])
            log_entry = f"Scheduled triage meeting: '{title}' at {slot['start_time'].strftime('%Y-%m-%d %H:%M')} with {attendee_list}"
            append_to_project_log(log_entry)
            
            return MeetingResponse(
                message=f"Meeting '{title}' scheduled for {slot['start_time'].strftime('%Y-%m-%d %H:%M')}",
                meeting_id=event["event_id"],
                scheduled_time=slot["start_time"].isoformat(),
                meeting_link=event["meeting_link"],
                attendees=[a["email"] for a in attendees]
            )
        else:
            # Just return the proposed time without scheduling
            return MeetingResponse(
                message=f"Proposed meeting time: {slot['start_time'].strftime('%Y-%m-%d %H:%M')}. Use auto_schedule=true to confirm.",
                scheduled_time=slot["start_time"].isoformat(),
                attendees=[a["email"] for a in attendees]
            )
    except Exception as e:
        logger.error(f"Error scheduling meeting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule meeting: {str(e)}")

@router.get("/schedule/blocked")
async def get_blocked_task_count():
    """
    Get the count of currently blocked tasks.
    """
    blocked = get_blocked_stories()
    return {"blocked_count": len(blocked), "blocked_stories": blocked}
