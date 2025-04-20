from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import os
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Models
class LogEntry(BaseModel):
    timestamp: str
    message: str
    date: str

class LogResponse(BaseModel):
    entries: List[LogEntry]
    total_entries: int

class LogFilterRequest(BaseModel):
    keyword: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    limit: Optional[int] = 50

# Helper functions
def read_project_log():
    """Read the project_log.md file and parse entries"""
    try:
        log_path = os.path.join("..", "project_log.md")
        
        # Read existing content
        with open(log_path, "r") as f:
            content = f.read()
            
        # Parse the log entries
        entries = []
        pattern = r'\- \*\*([\d\u2011\-\s:]+)\*\*: (.+)'
        
        for match in re.finditer(pattern, content):
            timestamp_str = match.group(1)
            message = match.group(2)
            
            # Extract date part only
            date_only = timestamp_str.split(" ")[0]
            
            entries.append(LogEntry(
                timestamp=timestamp_str,
                message=message,
                date=date_only
            ))
            
        return entries
    except Exception as e:
        logger.error(f"Error reading project log: {e}")
        return []

def append_to_project_log(entry):
    """Append an entry to the project_log.md file"""
    try:
        log_path = os.path.join("..", "project_log.md")
        
        # Read existing content
        with open(log_path, "r") as f:
            content = f.read()
        
        # Format the timestamp with Unicode hyphens to match style
        timestamp = datetime.now().strftime('%Y\u2011%m\u2011%d %H:%M')
        
        # Append new entry
        with open(log_path, "w") as f:
            f.write(f"{content}\n- **{timestamp}**: {entry}")
            
        logger.info(f"Added entry to project_log.md: {entry}")
        return True
    except Exception as e:
        logger.error(f"Failed to update project log: {e}")
        return False

def filter_log_entries(entries, filters):
    """Filter log entries based on the provided filters"""
    filtered_entries = entries
    
    # Filter by keyword
    if filters.keyword:
        keyword = filters.keyword.lower()
        filtered_entries = [e for e in filtered_entries if keyword in e.message.lower()]
    
    # Filter by date range
    if filters.date_from:
        try:
            date_from = datetime.strptime(filters.date_from, '%Y-%m-%d').date()
            filtered_entries = [
                e for e in filtered_entries 
                if datetime.strptime(e.date.replace('\u2011', '-'), '%Y-%m-%d').date() >= date_from
            ]
        except ValueError:
            # Invalid date format, ignore this filter
            pass
            
    if filters.date_to:
        try:
            date_to = datetime.strptime(filters.date_to, '%Y-%m-%d').date()
            filtered_entries = [
                e for e in filtered_entries 
                if datetime.strptime(e.date.replace('\u2011', '-'), '%Y-%m-%d').date() <= date_to
            ]
        except ValueError:
            # Invalid date format, ignore this filter
            pass
    
    # Apply limit
    if filters.limit and filters.limit > 0:
        filtered_entries = filtered_entries[:filters.limit]
        
    return filtered_entries

# Routes
@router.get("/log", response_model=LogResponse)
async def get_project_log():
    """Get all entries from the project log"""
    entries = read_project_log()
    
    # Return in reverse chronological order (newest first)
    entries.reverse()
    
    return LogResponse(
        entries=entries,
        total_entries=len(entries)
    )

@router.post("/log/filter", response_model=LogResponse)
async def filter_project_log(filters: LogFilterRequest):
    """Get filtered entries from the project log"""
    all_entries = read_project_log()
    
    # Apply filters
    filtered_entries = filter_log_entries(all_entries, filters)
    
    # Return in reverse chronological order (newest first)
    filtered_entries.reverse()
    
    return LogResponse(
        entries=filtered_entries,
        total_entries=len(filtered_entries)
    )

@router.post("/log/entry")
async def add_log_entry(entry: str):
    """Add a new entry to the project log (for testing)"""
    if not entry or entry.strip() == "":
        raise HTTPException(status_code=400, detail="Log entry cannot be empty")
        
    success = append_to_project_log(entry)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add log entry")
        
    return {"message": "Log entry added successfully"}
