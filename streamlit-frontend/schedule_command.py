def handle_schedule_command():
    import streamlit as st
    import time
    import os
    import sys
    from datetime import datetime, timedelta
    
    # Add project root to path for imports if running this file directly
    if __name__ == "__main__":
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from api_service import ApiService
    from helpers import load_tasks, log_action
    
    st.header("Meeting Scheduler")
    st.subheader("Schedule Triage Meetings")
    
    # Load tasks that might need discussion
    tasks = load_tasks()
    
    # Filter for tasks that might need triage (high priority or blocking)
    critical_tasks = [task for task in tasks if task["Status"] != "Done" and 
                      (task["Priority"] == "High" or 
                       "blocker" in task.get("Details", "").lower() or
                       "blocked" in task.get("Details", "").lower())]
    
    # Meeting configuration
    meeting_title = st.text_input("Meeting Title", "Triage Meeting")
    
    # If we have critical tasks, show them as options
    if critical_tasks:
        st.markdown("### Critical Tasks to Discuss")
        
        selected_tasks = []
        for task in critical_tasks:
            if st.checkbox(f"{task['Task ID']}: {task['Title']}", key=f"task_{task['Task ID']}"):
                selected_tasks.append(task)
        
        if selected_tasks:
            combined_title = f"{meeting_title}: {', '.join([t['Task ID'] for t in selected_tasks[:2]])}"
            if len(selected_tasks) > 2:
                combined_title += f" +{len(selected_tasks)-2} more"
            
            st.caption(f"Meeting will be titled: {combined_title}")
            meeting_title = combined_title
    
    # Team members selection
    st.subheader("Attendees")
    col1, col2 = st.columns(2)
    with col1:
        required_attendees = st.text_area("Required Attendees (one email per line)")
    with col2:
        optional_attendees = st.text_area("Optional Attendees (one email per line)")
    
    # Meeting date and time
    st.subheader("Meeting Schedule")
    col1, col2, col3 = st.columns(3)
    with col1:
        meeting_date = st.date_input("Meeting Date", value=datetime.now() + timedelta(days=1))
    with col2:
        meeting_time = st.time_input("Meeting Time", value=datetime.strptime("09:00", "%H:%M").time())
    with col3:
        duration_minutes = st.selectbox("Duration", [15, 30, 45, 60, 90], index=1)
    
    # Meeting location
    location_type = st.radio("Meeting Type", ["Virtual", "In-Person"])
    
    if location_type == "Virtual":
        meeting_platform = st.selectbox("Meeting Platform", ["Microsoft Teams", "Zoom", "Google Meet", "Webex"])
        if meeting_platform == "Microsoft Teams":
            meeting_location = "Microsoft Teams (link will be generated)"
        elif meeting_platform == "Zoom":
            meeting_location = "Zoom (link will be generated)"
        elif meeting_platform == "Google Meet":
            meeting_location = "Google Meet (link will be generated)"
        else:
            meeting_location = "Webex (link will be generated)"
    else:
        meeting_location = st.text_input("Meeting Room", "Conference Room A")
    
    # Meeting agenda
    st.subheader("Meeting Details")
    meeting_agenda = st.text_area("Agenda", 
                                placeholder="1. Review high-priority tasks\n2. Discuss blockers\n3. Agree on action items",
                                value=f"1. Review high-priority tasks\n2. Discuss blockers\n3. Agree on action items" if critical_tasks else "")
    
    meeting_notes = st.text_area("Additional Notes", placeholder="Please bring any relevant documentation")
    
    # Schedule the meeting
    if st.button("Schedule Meeting"):
        if not meeting_title:
            st.warning("Please enter a meeting title")
        elif not required_attendees:
            st.warning("Please add at least one required attendee")
        else:
            try:
                with st.spinner("Scheduling meeting..."):
                    # In a real implementation, we'd call the backend API
                    # Here we'll simulate the meeting creation for demonstration
                    time.sleep(1.5)  # Simulate API call
                
                # Prepare the attendee list
                required_list = [email.strip() for email in required_attendees.split("\n") if email.strip()]
                optional_list = [email.strip() for email in optional_attendees.split("\n") if email.strip()]
                
                meeting_datetime = datetime.combine(meeting_date, meeting_time)
                end_time = meeting_datetime + timedelta(minutes=duration_minutes)
                
                # Success message with meeting details
                st.success("Meeting scheduled successfully!")
                
                # Display meeting details in a nice card format
                st.markdown(f"""
                ### Meeting Scheduled

                **{meeting_title}**  
                📅 {meeting_datetime.strftime('%A, %B %d, %Y')}  
                ⏰ {meeting_datetime.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}  
                📍 {meeting_location}  
                
                **Attendees:** {len(required_list) + len(optional_list)} participants
                """)
                
                # Generate a fake meeting link for demonstration
                if location_type == "Virtual":
                    platform_domains = {
                        "Microsoft Teams": "teams.microsoft.com", 
                        "Zoom": "zoom.us", 
                        "Google Meet": "meet.google.com",
                        "Webex": "webex.com"
                    }
                    
                    fake_id = "".join([str(x) for x in range(10)])
                    meeting_link = f"https://{platform_domains[meeting_platform]}/meeting/{fake_id}"
                    
                    st.code(meeting_link)
                    st.markdown(f"[Join Meeting]({meeting_link})")
                
                # Show attendee details
                with st.expander("Attendee Details"):
                    st.markdown("### Required Attendees")
                    for attendee in required_list:
                        st.markdown(f"- {attendee}")
                        
                    if optional_list:
                        st.markdown("### Optional Attendees")
                        for attendee in optional_list:
                            st.markdown(f"- {attendee}")
                
                # Show agenda
                if meeting_agenda:
                    with st.expander("Meeting Agenda"):
                        st.markdown(meeting_agenda)
                
                # Add calendar integration options
                st.subheader("Calendar Integration")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Add to Google Calendar"):
                        st.success("Added to Google Calendar")
                with col2:
                    if st.button("Add to Outlook"):
                        st.success("Added to Outlook Calendar")
                with col3:
                    if st.button("Download iCal (.ics)"):
                        st.success("Calendar invitation downloaded")
                
                # Log the action using the imported function
                log_action(f"Triage meeting '{meeting_title}' scheduled for {meeting_datetime.strftime('%Y-%m-%d %H:%M')}")
                
                # Update project_log.md according to windsurf spec
                ApiService._append_to_project_log(f"/schedule – Triage meeting for {len(required_list)} team members scheduled for {meeting_datetime.strftime('%Y-%m-%d %H:%M')}")
                
            except Exception as e:
                st.error(f"Error scheduling meeting: {str(e)}")
