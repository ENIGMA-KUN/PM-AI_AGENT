"""
Gemini AI integration for the PM-Agent.
This module provides utilities for interacting with Google's Gemini API.
Following windsurf conventions: kebab-case filename, camelCase module usage.
"""

import os
import logging
import json
from datetime import datetime
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables")
    # Use a placeholder instead of hardcoding a real key
    GEMINI_API_KEY = "PLACEHOLDER_API_KEY_MISSING_FROM_ENV"
    logger.error("No GEMINI_API_KEY provided. Please add it to your .env file")

# Configure the Gemini model
genai.configure(api_key=GEMINI_API_KEY)

def parse_plan_with_gemini(plan_text: str) -> Dict[str, Any]:
    """
    Use Gemini to parse a natural language plan description into structured data.
    
    Example input: "Redesign landing page by Sep-05; Dev: Alice,Bob; Mktg: Carol"
    
    Returns a structured plan with title, due date, and assigned team members.
    """
    try:
        # Create a prompt for Gemini
        prompt = f"""
        Parse the following project plan text into a structured format.
        
        TEXT: {plan_text}
        
        Extract the following information:
        1. Title of the project/task
        2. Due date (convert any date format to YYYY-MM-DD)
        3. Team members and their roles
        
        Return the information in the following JSON format:
        {{
            "title": "The project title",
            "due_date": "YYYY-MM-DD",
            "team_members": [
                {{ "name": "Name1", "role": "Role1" }},
                {{ "name": "Name2", "role": "Role2" }}
            ]
        }}
        
        Only return the JSON, no other text.
        """
        
        # Call Gemini API directly
        model = genai.GenerativeModel(model_name="gemini-pro")
        response = model.generate_content(prompt)
        result = response.text
        
        # Parse the result
        parsed_data = json.loads(result)
        
        # Log the successful parsing
        logger.info(f"Successfully parsed plan: {parsed_data['title']}")
        
        # Update project log
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "project_log.md"), "a") as log_file:
            timestamp = datetime.now().strftime("%Y‑%m‑%d %H:%M")
            log_file.write(f"- **{timestamp}**: Gemini AI parsed plan: {parsed_data['title']}\n")
            
        return parsed_data
        
    except Exception as e:
        logger.error(f"Error parsing plan with Gemini: {e}")
        # Return a fallback structure
        return {
            "title": plan_text[:30] + "..." if len(plan_text) > 30 else plan_text,
            "due_date": "2025-12-31",
            "team_members": [{"name": "Unassigned", "role": "Developer"}]
        }

def get_completion(prompt: str) -> str:
    """
    Get a simple completion from Gemini for a given prompt.
    """
    try:
        model = genai.GenerativeModel(model_name="gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error getting completion from Gemini: {e}")
        return f"Error generating response: {str(e)}"
