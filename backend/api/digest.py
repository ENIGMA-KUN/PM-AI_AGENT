from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
import logging
import base64
from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import io
import pandas as pd
from fpdf import FPDF
import tempfile
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Models
class DigestRequest(BaseModel):
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    include_charts: bool = True
    include_blockers: bool = True
    title: Optional[str] = "Project Status Report"

class DigestResponse(BaseModel):
    message: str
    pdf_path: Optional[str] = None
    charts: Optional[Dict[str, str]] = None  # Base64 encoded chart images

# Helper functions
def load_plan_data():
    """Load the current plan data to analyze task status."""
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

def read_project_log():
    """Read the project_log.md file and parse entries"""
    try:
        log_path = os.path.join("..", "project_log.md")
        
        # Read existing content
        with open(log_path, "r") as f:
            content = f.read()
            
        # Parse the log entries
        entries = []
        import re
        pattern = r'\- \*\*([\d\u2011\-\s:]+)\*\*: (.+)'
        
        for match in re.finditer(pattern, content):
            timestamp_str = match.group(1)
            message = match.group(2)
            
            # Convert Unicode hyphens to regular hyphens for parsing
            timestamp_str = timestamp_str.replace('\u2011', '-')
            
            # Parse the timestamp
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M')
                entries.append({
                    "timestamp": timestamp,
                    "message": message
                })
            except ValueError:
                logger.warning(f"Could not parse timestamp: {timestamp_str}")
        
        return entries
    except Exception as e:
        logger.error(f"Error reading project log: {e}")
        return []

def generate_status_chart(plan_data):
    """Generate a chart showing task status distribution."""
    # Count tasks by status
    status_counts = {}
    for task in plan_data.get("tasks", []):
        status = task.get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Create the chart
    plt.figure(figsize=(8, 6))
    
    # Choose colors for each status
    colors = {
        "Todo": "lightblue", 
        "InProgress": "orange", 
        "Done": "lightgreen", 
        "Blocked": "salmon",
        "Unknown": "lightgray"
    }
    
    # If no tasks, add a dummy value
    if not status_counts:
        status_counts["No Data"] = 1
        colors["No Data"] = "lightgray"
    
    # Create pie chart
    labels = list(status_counts.keys())
    sizes = list(status_counts.values())
    chart_colors = [colors.get(status, "lightgray") for status in labels]
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=chart_colors)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Task Status Distribution')
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    
    # Convert to base64 string
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str

def generate_burndown_chart(log_entries, start_date=None, end_date=None):
    """Generate a burndown chart showing task completion over time."""
    # Filter log entries to find task completion events
    completion_events = []
    
    for entry in log_entries:
        # Look for entries that mention completing a task
        if "completed" in entry["message"].lower() or "done" in entry["message"].lower():
            completion_events.append(entry)
    
    # If no events, create a sample chart
    if not completion_events:
        # Create some sample data
        today = datetime.now()
        dates = [today - timedelta(days=i) for i in range(7, 0, -1)]
        remaining = [10, 8, 7, 6, 5, 3, 2]
        
        plt.figure(figsize=(10, 6))
        plt.plot(dates, remaining, marker='o', linestyle='-', color='blue', label='Remaining Tasks')
        
        # Add ideal line
        plt.plot([dates[0], dates[-1]], [remaining[0], 0], linestyle='--', color='red', label='Ideal Burndown')
        
        plt.xlabel('Date')
        plt.ylabel('Tasks Remaining')
        plt.title('Project Burndown Chart (Sample Data)')
        plt.legend()
        plt.grid(True)
        
        # Format dates nicely
        import matplotlib.dates as mdates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        
        # Convert to base64 string
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return img_str
    
    # If we have real data, create an actual burndown chart
    # (Implementation would go here, but simplified for demo)
    return generate_status_chart(load_plan_data())  # Simplified: return the status chart for now

def create_pdf_report(title, plan_data, log_entries, charts=None, include_blockers=True):
    """Generate a PDF report with project status, charts, and logs."""
    try:
        # Create a PDF object
        pdf = FPDF()
        pdf.add_page()
        
        # Set up fonts
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, title, ln=True, align='C')
        pdf.ln(5)
        
        # Add date
        pdf.set_font("Arial", '', 10)
        pdf.cell(190, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.ln(5)
        
        # Project Overview Section
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, "Project Overview", ln=True)
        pdf.ln(2)
        
        # Task summary
        pdf.set_font("Arial", '', 10)
        total_tasks = len(plan_data.get("tasks", []))
        completed_tasks = sum(1 for t in plan_data.get("tasks", []) if t.get("status") == "Done")
        in_progress = sum(1 for t in plan_data.get("tasks", []) if t.get("status") == "InProgress")
        
        pdf.cell(190, 10, f"Total Tasks: {total_tasks}", ln=True)
        pdf.cell(190, 10, f"Completed Tasks: {completed_tasks}", ln=True)
        pdf.cell(190, 10, f"In Progress: {in_progress}", ln=True)
        # Fix division by zero error with a conditional check
        completion_rate = (completed_tasks/total_tasks*100) if total_tasks > 0 else 0
        pdf.cell(190, 10, f"Completion Rate: {completion_rate:.1f}%", ln=True)
        pdf.ln(5)
        
        # Add status chart if available
        if charts and "status_chart" in charts:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(190, 10, "Status Chart", ln=True)
            
            # Save base64 image to temp file
            temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_img.write(base64.b64decode(charts["status_chart"]))
            temp_img.close()
            
            # Add image to PDF
            pdf.image(temp_img.name, x=10, y=None, w=180)
            pdf.ln(5)
            
            # Clean up temp file
            os.unlink(temp_img.name)
        
        # Add burndown chart if available
        if charts and "burndown_chart" in charts:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(190, 10, "Burndown Chart", ln=True)
            
            # Save base64 image to temp file
            temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_img.write(base64.b64decode(charts["burndown_chart"]))
            temp_img.close()
            
            # Add image to PDF
            pdf.image(temp_img.name, x=10, y=None, w=180)
            pdf.ln(5)
            
            # Clean up temp file
            os.unlink(temp_img.name)
        
        # Blockers section
        if include_blockers:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(190, 10, "Blockers and Risks", ln=True)
            pdf.ln(2)
            
            # List tasks that are blocked or have risks
            blocked_tasks = [t for t in plan_data.get("tasks", []) if t.get("status") == "Blocked"]
            
            if blocked_tasks:
                pdf.set_font("Arial", '', 10)
                for task in blocked_tasks:
                    pdf.set_font("Arial", 'B', 10)
                    pdf.cell(190, 10, f"{task.get('id', 'Unknown ID')}: {task.get('title', 'Untitled')}", ln=True)
                    
                    pdf.set_font("Arial", '', 10)
                    pdf.multi_cell(190, 10, f"Blocker: {task.get('blocker_description', 'No details provided')}")
                    pdf.ln(2)
            else:
                pdf.set_font("Arial", '', 10)
                pdf.cell(190, 10, "No blockers identified at this time.", ln=True)
        
        # Recent Activity Log
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, "Recent Activity", ln=True)
        pdf.ln(2)
        
        # Show last 10 log entries
        recent_logs = sorted(log_entries, key=lambda x: x["timestamp"], reverse=True)[:10]
        
        if recent_logs:
            pdf.set_font("Arial", '', 10)
            for entry in recent_logs:
                time_str = entry["timestamp"].strftime('%Y-%m-%d %H:%M')
                pdf.set_font("Arial", 'B', 8)
                pdf.cell(190, 10, time_str, ln=True)
                
                pdf.set_font("Arial", '', 10)
                pdf.multi_cell(190, 10, entry["message"])
                pdf.ln(2)
        else:
            pdf.set_font("Arial", '', 10)
            pdf.cell(190, 10, "No recent activity logged.", ln=True)
        
        # Save the PDF to a temporary file
        report_dir = os.path.join("data", "reports")
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_path = os.path.join(report_dir, f"project_report_{timestamp}.pdf")
        pdf.output(pdf_path)
        
        return pdf_path
    except Exception as e:
        logger.error(f"Error creating PDF report: {e}")
        raise

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
@router.post("/digest", response_model=DigestResponse)
async def generate_digest(request: DigestRequest):
    """
    Generate a project status digest report with charts and logs.
    
    - `start_date`: Optional start date filter (YYYY-MM-DD)
    - `end_date`: Optional end date filter (YYYY-MM-DD)
    - `include_charts`: Whether to include charts in the response
    - `include_blockers`: Whether to include blocker information
    - `title`: Report title
    """
    try:
        # Load data
        plan_data = load_plan_data()
        log_entries = read_project_log()
        
        # Generate charts
        charts = {}
        if request.include_charts:
            charts["status_chart"] = generate_status_chart(plan_data)
            charts["burndown_chart"] = generate_burndown_chart(
                log_entries, 
                start_date=request.start_date, 
                end_date=request.end_date
            )
        
        # Create PDF report
        pdf_path = create_pdf_report(
            request.title,
            plan_data,
            log_entries,
            charts=charts,
            include_blockers=request.include_blockers
        )
        
        # Log the action
        append_to_project_log(f"Generated digest report: '{request.title}'")
        
        return DigestResponse(
            message=f"Report '{request.title}' generated successfully",
            pdf_path=pdf_path,
            charts=charts if request.include_charts else None
        )
    except Exception as e:
        logger.error(f"Error generating digest: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/digest/download/{filename}")
async def download_digest(filename: str):
    """
    Download a generated report PDF by filename.
    """
    report_dir = os.path.join("data", "reports")
    file_path = os.path.join(report_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(file_path, media_type="application/pdf", filename=filename)
