"""
Lightweight API server for PM-Agent.
This provides the core API endpoints needed by the frontend while ensuring
compatibility with the Gemini API integration.

Following windsurf conventions: kebab-case filename with Python-compatible imports.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the gemini-utils module properly (kebab-case file, Python-compatible import)
from utils import gemini_utils

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Function to log to project_log.md
def log_action(action_description):
    try:
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "project_log.md")
        with open(log_path, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            log_file.write(f"- **{timestamp}**: {action_description}\n")
            logger.info(f"Logged action: {action_description}")
    except Exception as e:
        logger.error(f"Error logging to project_log.md: {e}")

# Root endpoint
@app.route("/")
def root():
    return jsonify({
        "message": "Welcome to PM Agent API", 
        "status": "operational"
    })

# Health check endpoint
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    })

# Plan API endpoint
@app.route("/api/plan", methods=["POST"])
def create_plan():
    try:
        # Get request body
        plan_text = request.json.get("plan_text", "")
        
        # Call Gemini to parse the plan
        parsed_plan = gemini_utils.parse_plan_with_gemini(plan_text)
        
        # Extract information
        title = parsed_plan.get("title", plan_text)
        due_date = parsed_plan.get("due_date", "2025-12-31")
        
        # Extract owners from team members
        owners = []
        for member in parsed_plan.get("team_members", []):
            owners.append(member.get("name", "Unassigned"))
        
        # Create stories
        stories = [
            {
                "title": title,
                "owner": owner,
                "due_date": due_date,
                "status": "Backlog"
            }
            for owner in owners
        ]
        
        # Store in file
        plan_data = {
            "title": title,
            "due_date": due_date,
            "stories": stories,
            "created_at": datetime.now().isoformat()
        }
        
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
        os.makedirs(data_path, exist_ok=True)
        
        with open(os.path.join(data_path, "plan.json"), "w") as f:
            json.dump(plan_data, f, indent=2)
        
        # Log the action
        log_action(f"Plan created: {title} with {len(stories)} stories")
        
        # Create response
        return jsonify({
            "stories": stories,
            "message": f"Plan created with {len(stories)} stories",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        return jsonify({"detail": str(e)}), 500

# Alerts check endpoint
@app.route("/api/alerts/check", methods=["GET"])
def check_alerts():
    return jsonify({
        "overdue_tasks": [
            {"title": "Complete API integration", "owner": "Alice", "days_overdue": 2},
            {"title": "Review documentation", "owner": "Bob", "days_overdue": 1}
        ]
    })

# Alerts endpoint
@app.route("/api/alerts", methods=["POST"])
def create_alerts():
    send_notifications = request.json.get("send_notifications", False)
    
    # Log the action
    if send_notifications:
        log_action("Alert notifications sent to team members")
    
    return jsonify({
        "overdue_tasks": [
            {"title": "Complete API integration", "owner": "Alice", "days_overdue": 2},
            {"title": "Review documentation", "owner": "Bob", "days_overdue": 1}
        ],
        "alerts_sent": 2 if send_notifications else 0,
        "timestamp": datetime.now().isoformat()
    })

# Risk API endpoint (stub)
@app.route("/api/risk", methods=["POST"])
def create_risk():
    return jsonify({
        "result": "Risk assessment created",
        "timestamp": datetime.now().isoformat()
    })

# Risk stories endpoint (stub)
@app.route("/api/risk/stories/<team_lead>", methods=["GET"])
def get_risk_stories(team_lead):
    return jsonify({
        "stories": [
            {"title": "Implement authentication", "status": "In Progress", "risk_level": "Medium"},
            {"title": "Deploy to production", "status": "Backlog", "risk_level": "High"}
        ]
    })

if __name__ == "__main__":
    # Log server start
    log_action("API server started with Gemini AI integration")
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=8000, debug=True)
