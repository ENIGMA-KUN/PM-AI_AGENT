import streamlit as st
import requests
import json
import os
import sys
import time
from datetime import datetime, timedelta
import pandas as pd

# Add path for local imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import services
from api_service import ApiService
from task_service import TaskService
from log_service import LogService

# Import command handlers from separate files for modularity
from digest_command import handle_digest_command
from schedule_command import handle_schedule_command

# Constants
API_BASE_URL = "http://localhost:8000/api"
BACKEND_URL = "http://localhost:8000"

# Configure Streamlit page
st.set_page_config(
    page_title="PM Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar navigation
st.sidebar.title("PM Agent")

# Function to log frontend actions to project_log.md
def log_action(action_description):
    try:
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project_log.md")
        
        # Read existing content
        with open(log_path, "r") as f:
            content = f.read()
        
        # Append new entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(log_path, "w") as f:
            f.write(content + f"\n- **{timestamp}**: {action_description}")
            
        print(f"Logged action: {action_description}")
    except Exception as e:
        print(f"Failed to update project log: {e}")

# API Connection functions
def check_api_health():
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        return False, str(e)

def load_tasks():
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "task.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading tasks: {e}")
        return []

# Command handlers
def handle_plan_command():
    st.header("Project Planning")
    st.subheader("Create or Update Project Plan")
    
    project_name = st.text_input("Project Name")
    project_description = st.text_area("Project Description")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")
    
    # Add team members selection according to project_core.md
    team_members = st.multiselect(
        "Team Members",
        ["PM", "Dev: Alice", "Dev: Bob", "Mktg: Carol", "QA", "DevOps", "Design", "Product"],
        default=["PM", "Dev: Alice", "Dev: Bob", "Mktg: Carol"]
    )
    
    if st.button("Generate Plan"):
        if not project_name:
            st.warning("Please enter a project name")
        else:
            try:
                # Using our ApiService to properly format plan_text
                with st.spinner("Generating plan..."):
                    result = ApiService.create_plan(
                        project_name=project_name,
                        description=project_description,
                        start_date=start_date.isoformat(),
                        end_date=end_date.isoformat(),
                        team_members=team_members
                    )
                
                if "error" in result:
                    st.error(f"Error generating plan: {result['error']}")
                    # Display more detailed troubleshooting info in an expander
                    with st.expander("API Request Details"):
                        st.code({
                            "plan_text": f"/plan {project_name} by {end_date.isoformat().split('T')[0]}; Team: {','.join(team_members)}; {project_description}"
                        }, language="json")
                else:
                    st.success("Plan generated successfully!")
                    
                    # Display stories in a Kanban board
                    if "stories" in result:
                        st.subheader("Kanban Board")
                        
                        # Create columns for Backlog, In Progress, Done
                        backlog_col, in_progress_col, done_col = st.columns(3)
                        
                        with backlog_col:
                            st.markdown("### 📋 Backlog")
                            for story in result["stories"]:
                                if story.get("status", "").lower() == "backlog":
                                    with st.container():
                                        st.markdown(f"**{story['title']}**")
                                        st.caption(f"Owner: {story['owner']} | Due: {story['due_date']}")
                        
                        with in_progress_col:
                            st.markdown("### 🔄 In Progress")
                            for story in result["stories"]:
                                if story.get("status", "").lower() == "inprogress":
                                    with st.container():
                                        st.markdown(f"**{story['title']}**")
                                        st.caption(f"Owner: {story['owner']} | Due: {story['due_date']}")
                        
                        with done_col:
                            st.markdown("### ✅ Done")
                            for story in result["stories"]:
                                if story.get("status", "").lower() == "done":
                                    with st.container():
                                        st.markdown(f"**{story['title']}**")
                                        st.caption(f"Owner: {story['owner']} | Due: {story['due_date']}")
                    
                    # Also display raw JSON in an expander
                    with st.expander("Raw Plan Data"):
                        st.json(result)
                    
                    # Log action
                    log_action(f"Plan generated for project '{project_name}' with Kanban board")
            except Exception as e:
                st.error(f"Error connecting to backend: {str(e)}")

def handle_risk_command():
    st.header("Risk Check-In")
    st.subheader("Send Risk Assessment to Team Leads")
    
    # Load current tasks from task.json
    tasks = load_tasks()
    
    # Filter tasks for active stories
    active_tasks = [task for task in tasks if task["Status"] != "Done"]
    
    if not active_tasks:
        st.warning("No active tasks found. Please create a plan first using the /plan command.")
        return
    
    # Option to send to all leads or select specific tasks
    risk_mode = st.radio("Risk Assessment Mode", ["Send Risk Modal to All Team Leads", "Check Specific Tasks"])
    
    if risk_mode == "Send Risk Modal to All Team Leads":
        # Identify team leads from task owners
        team_leads = set()
        for task in active_tasks:
            # Extract details based on task.json format
            details = task.get("Details", "")
            if "Dev:" in details:
                for dev in [part.strip() for part in details.split(";") if "Dev:" in part]:
                    leads = [lead.strip() for lead in dev.replace("Dev:", "").split(",")]
                    team_leads.update(leads)
            elif "Team:" in details:
                for team in [part.strip() for part in details.split(";") if "Team:" in part]:
                    leads = [lead.strip() for lead in team.replace("Team:", "").split(",")]
                    team_leads.update(leads)
        
        team_leads = list(team_leads) if team_leads else ["Default Lead"]
        
        # Show dropdown to choose leads
        selected_leads = st.multiselect("Select Team Leads to Notify", team_leads, default=team_leads)
        additional_recipients = st.text_input("Additional Recipients (comma-separated emails)")
        
        # Combine selected leads and additional recipients
        all_recipients = selected_leads.copy()
        if additional_recipients:
            all_recipients.extend([r.strip() for r in additional_recipients.split(",")])
        
        # Modal message
        modal_message = st.text_area("Risk Check-In Message", 
                                  "Please review the following stories and indicate if they are on track. For any blockers, please provide details.")
        
        # UI Mockup of the modal that will be sent
        with st.expander("Preview Risk Modal"):
            st.markdown("### ⚠️ Risk Assessment Modal")
            for task in active_tasks[:3]:  # Preview first 3 tasks
                st.markdown(f"**{task['Task ID']}: {task['Title']}**")
                cols = st.columns(2)
                with cols[0]:
                    st.checkbox("On Track?", key=f"preview_{task['Task ID']}_ontrack")
                with cols[1]:
                    st.selectbox("If Not On Track, Reason:", 
                             ["N/A", "Need Discussion", "Missing Estimated Completion", "Technical Blocker", "External Dependency"], 
                             key=f"preview_{task['Task ID']}_reason")
            
            st.button("Submit (Demo)", disabled=True)
            st.caption("This is just a preview of what team leads will receive.")
            
        if st.button("Send Risk Check-In to Selected Leads"):
            if not all_recipients:
                st.warning("Please select at least one team lead or add additional recipients")
            else:
                try:
                    # For each team lead, create a risk check structure
                    for lead in all_recipients:
                        with st.spinner(f"Sending risk modal to {lead}..."):
                            # In a real system, this would email the modal to the lead
                            # Here we'll simulate it with a success message
                            # Log the action
                            log_action(f"Risk check-in modal sent to {lead} for {len(active_tasks)} stories")
                    
                    # Show confirmation
                    st.success(f"Risk check-in modals sent successfully to {len(all_recipients)} team leads!")
                    st.markdown(f"### Modals sent to:")
                    for lead in all_recipients:
                        st.markdown(f"- {lead}")
                        
                    # Explain next steps
                    st.info("**Next Steps**: Team leads will receive a modal where they can mark each story as on track or blocked. Any blocker will turn the story red on the Kanban board and trigger alerts.")
                    
                    # Show a simulated response
                    with st.expander("Simulated Team Lead Response"):
                        st.markdown("### Simulated Response from Team Lead")
                        blocker_idx = 1 if len(active_tasks) > 1 else 0
                        if active_tasks:
                            for i, task in enumerate(active_tasks[:3]):
                                is_blocker = (i == blocker_idx)  # Make the second task a blocker for demonstration
                                st.markdown(f"**{task['Task ID']}: {task['Title']}**")
                                st.markdown(f"**On Track:** {'❌ No' if is_blocker else '✅ Yes'}")
                                if is_blocker:
                                    st.markdown("**Reason:** Need Discussion")
                                    st.markdown("**Details:** Requirement clarification needed from stakeholders")
                except Exception as e:
                    st.error(f"Error sending risk check-in: {str(e)}")
    else:
        # Select specific tasks for risk assessment
        task_options = [f"{task['Task ID']}: {task['Title']}" for task in active_tasks]
        selected_task = st.selectbox("Select Task for Risk Assessment", task_options)
        
        recipients = st.text_input("Recipients (comma-separated emails)")
        team_lead = st.text_input("Primary Team Lead", value="" if not recipients else recipients.split(",")[0].strip())
        include_message = st.text_area("Additional Message")
        
        if st.button("Send Risk Check-In for Selected Task"):
            if not selected_task:
                st.warning("Please select a task")
            elif not recipients:
                st.warning("Please enter at least one recipient")
            else:
                try:
                    task_id = selected_task.split(":")[0].strip()
                    recipient_list = [email.strip() for email in recipients.split(",")]
                    
                    with st.spinner("Sending risk check-in..."):
                        result = ApiService.send_risk_checkin(
                            task_id=task_id,
                            recipients=recipient_list,
                            message=include_message
                        )
                    
                    if "error" in result:
                        st.error(f"Error sending risk check-in: {result['error']}")
                        # Display more detailed troubleshooting info in an expander
                        with st.expander("API Request Details"):
                            st.code({
                                "task_id": task_id,
                                "recipients": recipient_list,
                                "team_lead": team_lead if team_lead else recipient_list[0] if recipient_list else "",
                                "message": include_message
                            }, language="json")
                    else:
                        st.success("Risk check-in sent successfully!")
                        
                        # Display result
                        if isinstance(result, dict):
                            st.json(result)
                        
                        # Log action
                        log_action(f"Risk check-in sent for {task_id}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {str(e)}")

def handle_alerts_command():
    st.header("Task Alerts")
    st.subheader("Daily Overdue Alerts")
    
    # Load current tasks from task.json
    tasks = load_tasks()
    
    # Add date filter for overdue tasks
    col1, col2 = st.columns(2)
    with col1:
        as_of_date = st.date_input("As of Date", datetime.now())
    with col2:
        alert_type = st.selectbox("Alert Type", ["All Alerts", "Overdue Tasks", "Upcoming Deadlines", "Blocked Tasks"])
    
    # For demo - parse approximate due dates from task details or description
    # In a real app, this would be pulled from actual task metadata
    overdue_tasks = []
    upcoming_tasks = []
    blocked_tasks = []
    
    for task in tasks:
        # Skip done tasks for overdue and upcoming
        if task["Status"] == "Done" and alert_type != "All Alerts":
            continue
            
        # Check for blocked tasks (by details)
        if "blocker" in task.get("Details", "").lower() or "blocked" in task.get("Details", "").lower():
            blocked_tasks.append(task)
            
        # Parse dates from description
        description = task.get("Description", "")
        details = task.get("Details", "")
        
        # Look for date patterns in text
        date_pattern = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}\b'
        all_text = f"{description} {details}"
        
        # For demo purposes: if high priority and not done, treat as overdue
        if task["Priority"] == "High" and task["Status"] != "Done":
            overdue_tasks.append(task)
        # Medium priority not done tasks are upcoming
        elif task["Priority"] == "Medium" and task["Status"] != "Done":
            upcoming_tasks.append(task)
    
    # Filter based on selected alert type
    display_tasks = []
    if alert_type == "All Alerts":
        display_tasks = overdue_tasks + upcoming_tasks + blocked_tasks
    elif alert_type == "Overdue Tasks":
        display_tasks = overdue_tasks
    elif alert_type == "Upcoming Deadlines":
        display_tasks = upcoming_tasks
    else:  # Blocked Tasks
        display_tasks = blocked_tasks
    
    # Remove duplicates while preserving order
    seen = set()
    unique_display_tasks = []
    for task in display_tasks:
        task_id = task["Task ID"]
        if task_id not in seen:
            seen.add(task_id)
            unique_display_tasks.append(task)
    
    if unique_display_tasks:
        st.write(f"Found {len(unique_display_tasks)} tasks that need attention:")
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["List View", "Card View"])
        
        with tab1:  # List View
            for task in unique_display_tasks:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Add icons based on alert type
                        icon = "🔴" if task in overdue_tasks else "🟠" if task in upcoming_tasks else "🟡"
                        st.markdown(f"{icon} **{task['Task ID']}: {task['Title']}**")
                        st.caption(f"Status: {task['Status']} | Priority: {task['Priority']}")
                    with col2:
                        if st.button("Send Alert", key=f"alert_{task['Task ID']}"):
                            st.session_state[f"selected_task_{task['Task ID']}"] = True
                    st.markdown("---")
        
        with tab2:  # Card View
            # Create grid for cards
            cols = st.columns(3)
            for i, task in enumerate(unique_display_tasks):
                with cols[i % 3]:
                    with st.container():
                        # Color based on priority
                        color = "#ff6b6b" if task["Priority"] == "High" else "#feca57" if task["Priority"] == "Medium" else "#1dd1a1"
                        st.markdown(f"<div style='border-left: 5px solid {color}; padding-left: 10px;'>"
                                   f"<h4>{task['Task ID']}: {task['Title']}</h4>"
                                   f"<p>Status: {task['Status']}</p>"
                                   f"<p>Priority: {task['Priority']}</p>"
                                   f"</div>", unsafe_allow_html=True)
        
        # Add bulk alert options
        st.subheader("📧 Send Bulk Alerts")
        recipients = st.text_input("Recipients (comma-separated emails)")
        include_message = st.text_area("Alert Message", f"ALERT: {len(unique_display_tasks)} tasks need attention as of {as_of_date.strftime('%Y-%m-%d')}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            send_email = st.checkbox("Email", True)  
        with col2:
            send_slack = st.checkbox("Slack")
        with col3:
            send_teams = st.checkbox("Teams")
            
        if st.button("Send Alerts"):
            if not recipients and send_email:
                st.warning("Please enter at least one recipient email for Email alerts")
            else:
                try:
                    channels = []
                    if send_email: channels.append("Email")
                    if send_slack: channels.append("Slack")
                    if send_teams: channels.append("Teams")
                    
                    with st.spinner("Sending alerts..."):
                        # In a real app, call the API here
                        time.sleep(1.5)  # Simulate API call
                    
                    st.success(f"Alerts sent via {', '.join(channels)}")
                    
                    # Show a preview of the sent alert
                    with st.expander("Alert Preview"):
                        st.markdown(f"### Task Alert: {as_of_date.strftime('%Y-%m-%d')}")
                        st.markdown(include_message)
                        st.markdown("#### Task Summary")
                        for i, task in enumerate(unique_display_tasks[:5]):  # Show first 5 tasks
                            st.markdown(f"{i+1}. **{task['Task ID']}**: {task['Title']} ({task['Status']})")
                        if len(unique_display_tasks) > 5:
                            st.caption(f"...and {len(unique_display_tasks) - 5} more tasks")
                    
                    # Log action
                    log_action(f"Alerts sent via {', '.join(channels)} for {len(unique_display_tasks)} tasks")
                    
                    # Update project_log.md according to windsurf spec
                    from api_service import ApiService
                    ApiService._append_to_project_log(f"/alerts – Daily alert sent for {len(unique_display_tasks)} tasks via {', '.join(channels)}")
                    
                except Exception as e:
                    st.error(f"Error sending alerts: {str(e)}")
    else:
        st.success("🎉 No tasks need attention. Everything is on track!")
        
        # Show a celebratory message in Streamlit
        st.balloons()

def handle_log_command():
    st.header("Project Log")
    st.subheader("View Project Activities")
    
    try:
        # Read the project log content
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project_log.md")
        with open(log_path, "r") as f:
            log_content = f.read()
        
        # Parse log entries and organize them
        import re
        pattern = r'\- \*\*(.*?)\*\*: (.+)'
        entries = []
        
        for match in re.finditer(pattern, log_content):
            timestamp_str = match.group(1)
            message = match.group(2)
            
            # Convert Unicode hyphens to regular hyphens for parsing
            timestamp_str = timestamp_str.replace('\u2011', '-')
            
            try:
                entries.append({
                    "timestamp": timestamp_str,
                    "message": message
                })
            except Exception:
                pass  # Skip unparseable entries
        
        # Add filtering options
        st.sidebar.header("Log Filters")
        filter_options = ["All Activities", "Plans", "Risk Check-ins", "Alerts", "Meetings", "Digests", "System Events"]
        selected_filter = st.sidebar.selectbox("Filter by Type", filter_options)
        
        # Create date range filter
        date_range = st.sidebar.date_input("Date Range", 
                                  [datetime.now().replace(day=1), datetime.now()],
                                  format="YYYY-MM-DD")
        
        # Display the log with a nice looking styled table
        st.markdown("## Activity Timeline")
        
        # Apply filters
        filtered_entries = entries
        if selected_filter != "All Activities":
            filter_keywords = {
                "Plans": ["/plan", "plan generated", "board created"],
                "Risk Check-ins": ["/risk", "blocker", "risk check-in", "team lead"],
                "Alerts": ["/alerts", "overdue", "notification"],
                "Meetings": ["/schedule", "meeting", "triage"],
                "Digests": ["/digest", "report", "stakeholder", "PDF"],
                "System Events": ["loaded", "created", "updated", "initialized"]
            }
            
            keywords = filter_keywords.get(selected_filter, [])
            filtered_entries = [entry for entry in entries if any(kw.lower() in entry["message"].lower() for kw in keywords)]
        
        # Sort entries by timestamp (newest first)
        filtered_entries.reverse()
        
        # Display entries in a stylized way
        for entry in filtered_entries:
            # Use different icons based on entry type
            icon = "📋"
            if "/plan" in entry["message"].lower() or "plan" in entry["message"].lower():
                icon = "🗓️"
            elif "/risk" in entry["message"].lower() or "blocker" in entry["message"].lower():
                icon = "⚠️"
            elif "/alerts" in entry["message"].lower() or "overdue" in entry["message"].lower():
                icon = "⏰"
            elif "/schedule" in entry["message"].lower() or "meeting" in entry["message"].lower():
                icon = "🔄"
            elif "/digest" in entry["message"].lower() or "report" in entry["message"].lower():
                icon = "📊"
            elif "loaded" in entry["message"].lower() or "created" in entry["message"].lower():
                icon = "🔧"
                
            # Create stylized entry
            st.markdown(f"### {icon} **{entry['timestamp']}**")
            st.markdown(f"{entry['message']}")
            st.markdown("---")
        
        if not filtered_entries:
            st.info("No matching log entries found. Try changing the filter options.")
        
        # Export options
        export_format = st.sidebar.selectbox("Export Format", ["None", "CSV", "PDF"])
        if export_format != "None" and st.sidebar.button("Export Log"):
            st.sidebar.success(f"Log exported as {export_format} (demo)")
        
        # Log this view in the project log
        log_action("Project log viewed")
        
    except Exception as e:
        st.error(f"Error loading project log: {str(e)}")
    
    col1, col2 = st.columns(2)
    with col1:
        meeting_date = st.date_input("Meeting Date")
    with col2:
        meeting_time = st.time_input("Meeting Time")
    
    duration_minutes = st.slider("Duration (minutes)", 15, 120, 30, step=15)
    
    if st.button("Schedule Meeting"):
        if not meeting_title:
            st.warning("Please enter a meeting title")
        elif not attendees:
            st.warning("Please enter at least one attendee")
        else:
            try:
                meeting_datetime = datetime.combine(meeting_date, meeting_time).isoformat()
                
                response = requests.post(
                    f"{API_BASE_URL}/schedule",
                    json={
                        "title": meeting_title,
                        "datetime": meeting_datetime,
                        "duration_minutes": duration_minutes,
                        "attendees": [email.strip() for email in attendees.split(",")]
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Meeting scheduled successfully!")
                    
                    if "meeting_link" in result:
                        st.markdown(f"Meeting Link: {result['meeting_link']}")
                    
                    # Log action
                    log_action(f"Triage meeting '{meeting_title}' scheduled")
                else:
                    st.error(f"Error scheduling meeting: {response.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {str(e)}")

# Application State
if "page" not in st.session_state:
    st.session_state.page = "home"

# Sidebar Navigation
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Plan (/plan)", "Risk (/risk)", "Alerts (/alerts)", "Log (/log)", "Digest (/digest)", "Schedule (/schedule)"]
)

# Check backend connectivity
api_status, health_info = check_api_health()
if api_status:
    st.sidebar.success("✅ Connected to backend")
    if health_info:
        st.sidebar.info(f"API Version: {health_info.get('version', 'Unknown')}")
else:
    st.sidebar.error("❌ Backend not connected")
    st.sidebar.warning("Make sure the backend is running on http://localhost:8000")
    if health_info:
        st.sidebar.error(f"Error: {health_info}")

# Page routing
if page == "Home":
    st.header("PM Agent Dashboard")
    st.subheader("Welcome to the Project Management Assistant")
    
    st.markdown("""
    Use the commands below to manage your project:
    
    - **/plan** - Generate project plan with Kanban board and tasks
    - **/risk** - Send risk check-in modals to team leads
    - **/alerts** - Check for overdue tasks and send notifications
    - **/log** - View the chronological project activity log
    - **/digest** - Generate PDF status reports for stakeholders
    - **/schedule** - Schedule triage meetings for blocked stories
    
    Navigate using the sidebar or enter commands in the chat below.
    """)
    
    # About section explaining how commands work in detail
    with st.expander("About PM Agent & Command Details"):
        st.markdown("""
        ## PM Agent - Windsurf Project Structure
        
        This application follows strict windsurf project architecture with kebab-case files and camelCase modules.
        All commands are tracked in `task.json` and logged in `project_log.md` to avoid module name errors and hallucinations.
        
        ### Detailed Command Usage:
        
        #### /plan Command
        Creates a structured project plan with tasks and timeline. The API expects:
        - **name**: Project name (required)
        - **description**: Project details (required)
        - **start_date/end_date**: ISO format dates (required)
        - **team**: Array of team members (required)
        
        #### /risk Command
        Sends risk assessment surveys to team leads about specific tasks:
        - **task_id**: ID from task.json (e.g., TSK-004) (required)
        - **recipients**: Email addresses for notifications (required)
        - **team_lead**: Primary contact for the risk assessment (required)
        - **message**: Additional context for the risk survey (optional)
        
        #### /alerts Command
        Checks for overdue tasks and sends notifications to owners:
        - **include_pending**: Whether to include tasks marked as Done (optional)
        - **send_notifications**: Whether to send messages to task owners (optional)
        
        #### /log Command
        Displays the chronological project activity log from `project_log.md`.
        All system actions are automatically logged with timestamps.
        
        #### /digest Command
        Generates status reports for stakeholders with metrics and visualizations:
        - **title**: Report name (required)
        - **recipients**: Email addresses to receive the report (optional)
        - **format**: Output format, defaulting to PDF (required)
        - **include_metrics/include_risks**: Content options (optional)
        
        #### /schedule Command
        Schedules triage meetings for teams to address blocked items:
        - **title**: Meeting title (required)
        - **datetime**: ISO format meeting time (required)
        - **duration_minutes**: Length of meeting (required)
        - **attendees**: List of participant emails (required)
        - **location**: Meeting venue, virtual or physical (required)
        
        ### Backend Connection
        
        The application connects to a FastAPI backend at http://localhost:8000 using properly structured
        requests that match the backend API expectations. Error handling ensures meaningful feedback when
        API calls fail.
        """)
    
    # Display tasks from task.json
    st.subheader("Current Tasks")
    tasks = load_tasks()
    
    # Create task dataframe
    if tasks:
        task_df = pd.DataFrame(tasks)
        st.dataframe(task_df[["Task ID", "Title", "Status", "Priority"]], use_container_width=True)
    else:
        st.info("No tasks found. Use /plan to create tasks.")
    
    # Simple chat interface
    st.subheader("Chat Interface")
    user_input = st.text_input("Enter a command (e.g., /plan, /risk, /alerts):")
    
    if user_input:
        if user_input.startswith("/plan"):
            st.session_state.page = "Plan (/plan)"
            st.rerun()
        elif user_input.startswith("/risk"):
            st.session_state.page = "Risk (/risk)"
            st.rerun()
        elif user_input.startswith("/alerts"):
            st.session_state.page = "Alerts (/alerts)"
            st.rerun()
        elif user_input.startswith("/log"):
            st.session_state.page = "Log (/log)"
            st.rerun()
        elif user_input.startswith("/digest"):
            st.session_state.page = "Digest (/digest)"
            st.rerun()
        elif user_input.startswith("/schedule"):
            st.session_state.page = "Schedule (/schedule)"
            st.rerun()
        else:
            st.warning(f"Unknown command: {user_input}")

elif page == "Plan (/plan)":
    handle_plan_command()
    
elif page == "Risk (/risk)":
    handle_risk_command()
    
elif page == "Alerts (/alerts)":
    handle_alerts_command()
    
elif page == "Log (/log)":
    handle_log_command()
    
elif page == "Digest (/digest)":
    handle_digest_command()
    
elif page == "Schedule (/schedule)":
    handle_schedule_command()

# Footer
st.sidebar.divider()
st.sidebar.caption("PM Agent v0.1.0")
st.sidebar.caption("© 2025 Project Management System")
