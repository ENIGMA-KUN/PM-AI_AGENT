"""
Helper functions and utilities for the PM Agent
To avoid circular imports, these functions are kept in a separate file
"""
import os
import json
import streamlit as st
from datetime import datetime

def load_tasks():
    """Load tasks from task.json"""
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "task.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading tasks: {e}")
        return []

def log_action(action_description):
    """Log action to project_log.md"""
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
