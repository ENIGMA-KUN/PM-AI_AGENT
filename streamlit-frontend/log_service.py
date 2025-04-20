import os
from datetime import datetime
from typing import List, Optional

class LogService:
    """Service for managing project log entries according to windsurf standards"""
    
    @staticmethod
    def get_log_path() -> str:
        """Get the absolute path to the project_log.md file"""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project_log.md")
    
    @staticmethod
    def read_log() -> str:
        """Read the entire project log"""
        try:
            with open(LogService.get_log_path(), "r") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading project log: {e}")
            return "# Project Log\n\n*No entries found*"
    
    @staticmethod
    def append_log_entry(action_description: str) -> bool:
        """Append a new entry to the project log"""
        try:
            log_path = LogService.get_log_path()
            
            # Read existing content
            content = LogService.read_log()
            
            # Append new entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(log_path, "w") as f:
                f.write(content + f"\n- **{timestamp}**: {action_description}")
                
            return True
        except Exception as e:
            print(f"Failed to update project log: {e}")
            return False
    
    @staticmethod
    def get_recent_entries(count: int = 10) -> List[str]:
        """Get the most recent log entries"""
        content = LogService.read_log()
        lines = content.split('\n')
        
        # Filter only entry lines (starting with '- **')
        entries = [line for line in lines if line.startswith("- **")]
        
        # Return most recent entries
        return entries[-count:] if count < len(entries) else entries
