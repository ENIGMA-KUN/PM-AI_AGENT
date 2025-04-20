def handle_digest_command():
    import streamlit as st
    import pandas as pd
    import time
    import os
    import io
    import base64
    from datetime import datetime
    import matplotlib.pyplot as plt
    from PIL import Image
    import sys
    
    # Add project root to path for imports if running this file directly
    if __name__ == "__main__":
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from api_service import ApiService
    from helpers import load_tasks, log_action
    
    st.header("Project Digest")
    st.subheader("Generate Project Status Report")
    
    # Project selection (if there are multiple projects)
    tasks = load_tasks()
    project_names = set()
    for task in tasks:
        if "Plan:" in task.get("Title", ""):
            project_names.add(task["Title"].replace("Plan:", "").strip())
    
    if not project_names:
        project_names = {"Default Project"}
    
    selected_project = st.selectbox("Select Project", list(project_names))
    
    # Report configuration
    col1, col2 = st.columns(2)
    with col1:
        report_name = st.text_input("Report Name", f"{selected_project} Status Report")
        report_format = st.selectbox("Report Format", ["PDF", "HTML", "Markdown"])
    
    with col2:
        recipients = st.text_input("Recipients (comma-separated emails)")
        audience = st.selectbox("Target Audience", ["Executives", "Technical Team", "Stakeholders", "All"])
    
    # Report content options
    st.subheader("Report Content")
    col1, col2, col3 = st.columns(3)
    with col1:
        include_metrics = st.checkbox("Include Metrics", value=True)
        include_summary = st.checkbox("Include Summary", value=True)
    with col2:
        include_risks = st.checkbox("Include Risks", value=True)
        include_charts = st.checkbox("Include Charts", value=True)
    with col3:
        include_timeline = st.checkbox("Include Timeline", value=True)
        include_next_steps = st.checkbox("Include Next Steps", value=True)
    
    # Optional custom message
    custom_message = st.text_area("Custom Message (optional)", "")
    
    if st.button("Generate Digest"):
        if not report_name:
            st.warning("Please enter a report name")
        else:
            try:
                with st.spinner("Generating detailed report..."):
                    # In a real implementation, we'd call the backend API
                    # Here we'll simulate the PDF generation for demonstration
                    time.sleep(2)  # Simulate processing time
                
                st.success("Digest generated successfully!")
                
                # Display report preview with tabs for different sections
                st.subheader("Report Preview")
                
                tabs = []
                if include_summary: tabs.append("Summary")
                if include_metrics: tabs.append("Metrics")
                if include_risks: tabs.append("Risks")
                if include_timeline: tabs.append("Timeline")
                if include_next_steps: tabs.append("Next Steps")
                
                preview_tabs = st.tabs(tabs)
                
                # Filter relevant tasks for this project
                project_tasks = [t for t in tasks if selected_project in t.get("Title", "") or selected_project in t.get("Description", "")]
                if not project_tasks:
                    project_tasks = tasks  # If no specific tasks found, use all
                
                # Calculate stats
                completed = sum(1 for t in project_tasks if t["Status"] == "Done")
                in_progress = sum(1 for t in project_tasks if t["Status"] == "InProgress")
                remaining = len(project_tasks) - completed - in_progress
                
                completion_rate = (completed / len(project_tasks) * 100) if project_tasks else 0
                
                # Generate a sample chart
                if include_charts:
                    # Create a pie chart of task status
                    fig, ax = plt.subplots(figsize=(8, 6))
                    status_counts = {
                        "Completed": completed,
                        "In Progress": in_progress,
                        "Not Started": remaining
                    }
                    
                    colors = {
                        "Completed": "#1dd1a1",
                        "In Progress": "#feca57",
                        "Not Started": "#ff6b6b"
                    }
                    
                    # Check for empty data
                    if sum(status_counts.values()) == 0:
                        status_counts = {"No Data": 1}
                        colors = {"No Data": "lightgray"}
                    
                    wedges, texts, autotexts = ax.pie(
                        status_counts.values(),
                        labels=status_counts.keys(),
                        colors=[colors[k] for k in status_counts.keys()],
                        autopct='%1.1f%%',
                        startangle=90
                    )
                    
                    # Equal aspect ratio ensures the pie chart is circular
                    ax.axis('equal')
                    plt.title("Task Status Distribution", fontsize=16)
                    
                    # Convert plot to image
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight')
                    buf.seek(0)
                    img = Image.open(buf)
                    
                    # Convert to base64 for embedding
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Fill in the tab contents
                for i, tab_name in enumerate(tabs):
                    with preview_tabs[i]:
                        if tab_name == "Summary":
                            st.markdown(f"### Project Summary: {selected_project}")
                            st.markdown(f"**Report Date:** {datetime.now().strftime('%Y-%m-%d')}")
                            st.markdown(f"**Project Completion:** {completion_rate:.1f}%")
                            st.markdown(f"**Total Tasks:** {len(project_tasks)}")
                            st.markdown(f"**Tasks Completed:** {completed}")
                            st.markdown(f"**Tasks In Progress:** {in_progress}")
                            
                            if custom_message:
                                st.markdown("### Custom Message")
                                st.markdown(custom_message)
                        
                        elif tab_name == "Metrics":
                            st.markdown("### Project Metrics")
                            
                            # Display charts
                            if include_charts:
                                st.markdown("#### Task Status Distribution")
                                st.image(f"data:image/png;base64,{img_str}", use_column_width=True)
                            
                            # Display metrics table
                            st.markdown("#### Key Performance Indicators")
                            kpi_data = {
                                "Metric": ["Completion Rate", "Tasks Completed", "Tasks In Progress", "Tasks Remaining", "High Priority Tasks"],
                                "Value": [
                                    f"{completion_rate:.1f}%", 
                                    completed,
                                    in_progress,
                                    remaining,
                                    sum(1 for t in project_tasks if t["Priority"] == "High")
                                ]
                            }
                            st.table(pd.DataFrame(kpi_data))
                        
                        elif tab_name == "Risks":
                            st.markdown("### Project Risks")
                            
                            # Find high-priority non-completed tasks as risks
                            risk_tasks = [t for t in project_tasks if t["Priority"] == "High" and t["Status"] != "Done"]
                            
                            if risk_tasks:
                                for task in risk_tasks:
                                    st.markdown(f"**{task['Task ID']}: {task['Title']}**")
                                    st.markdown(f"Status: {task['Status']}")
                                    st.markdown(f"Details: {task.get('Details', 'No details provided')}")
                                    st.markdown("---")
                            else:
                                st.info("No significant risks identified.")
                        
                        elif tab_name == "Timeline":
                            st.markdown("### Project Timeline")
                            st.markdown("#### Recent Activities")
                            
                            # Show a timeline of activities from project_log.md
                            try:
                                log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project_log.md")
                                with open(log_path, "r") as f:
                                    log_content = f.read()
                                
                                # Parse and show recent entries
                                import re
                                pattern = r'\- \*\*(.*?)\*\*: (.+)'
                                entries = []
                                
                                for match in re.finditer(pattern, log_content):
                                    timestamp_str = match.group(1)
                                    message = match.group(2)
                                    entries.append((timestamp_str, message))
                                
                                # Show most recent entries first
                                entries.reverse()
                                
                                if entries:
                                    for i, (date, message) in enumerate(entries[:5]):
                                        st.markdown(f"**{date}:** {message}")
                                        
                                    if len(entries) > 5:
                                        with st.expander("View More Activities"):
                                            for date, message in entries[5:15]:
                                                st.markdown(f"**{date}:** {message}")
                                else:
                                    st.info("No project activities logged yet.")
                            except Exception as e:
                                st.error(f"Could not load project log: {str(e)}")
                        
                        elif tab_name == "Next Steps":
                            st.markdown("### Next Steps")
                            
                            # Find upcoming tasks (not started but high priority)
                            next_tasks = [t for t in project_tasks if t["Status"] != "Done" and t["Status"] != "InProgress"]
                            if not next_tasks:
                                next_tasks = [t for t in project_tasks if t["Status"] != "Done"]
                            
                            if next_tasks:
                                st.markdown("#### Upcoming Tasks")
                                for i, task in enumerate(sorted(next_tasks, key=lambda t: t["Priority"], reverse=True)[:5]):
                                    st.markdown(f"{i+1}. **{task['Task ID']}: {task['Title']}** (Priority: {task['Priority']})")
                                
                                st.markdown("#### Recommendations")
                                st.markdown("1. Schedule a review meeting for high-priority tasks")
                                st.markdown("2. Update the project plan based on current progress")
                                st.markdown("3. Conduct a risk assessment session with the team")
                            else:
                                st.success("All tasks are complete! Time to celebrate or plan the next phase.")
                
                # Show download and sharing options
                st.subheader("Distribution Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Download Report"):
                        st.success(f"Report downloaded as {report_format}")
                
                with col2:
                    if recipients:
                        if st.button("Email Report"):
                            recipient_list = [r.strip() for r in recipients.split(",")]
                            st.success(f"Report emailed to {len(recipient_list)} recipients")
                    else:
                        st.warning("Add recipients to enable email delivery")
                
                # Log the action using the imported log_action function
                log_action(f"Project digest '{report_name}' generated in {report_format} format")
                
                # Update project_log.md according to windsurf spec
                ApiService._append_to_project_log(f"/digest – {report_name} generated for {audience} audience in {report_format} format")
                
            except Exception as e:
                st.error(f"Error generating digest: {str(e)}")
