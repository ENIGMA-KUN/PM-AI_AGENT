"""
Direct Gemini API integration for PM-Agent.
This module provides a clean, dependency-minimal way to interact with Google's Gemini API.
Following windsurf conventions: kebab-case filename, camelCase module usage.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
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
    GEMINI_API_KEY = "PLACEHOLDER_API_KEY_MISSING"
    logger.error("No GEMINI_API_KEY provided. Please add it to your .env file")

# Configure the Gemini model
genai.configure(api_key=GEMINI_API_KEY)

def parse_plan(plan_text: str) -> Dict[str, Any]:
    """
    Parse a natural language plan description into structured data using Gemini API.
    
    Args:
        plan_text: String containing the plan description
        
    Returns:
        Dictionary with parsed plan data
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
        
        logger.info(f"Successfully parsed plan: {parsed_data['title']}")
        return parsed_data
        
    except Exception as e:
        logger.error(f"Error parsing plan with Gemini: {e}")
        # Return a fallback structure
        return {
            "title": plan_text[:30] + "..." if len(plan_text) > 30 else plan_text,
            "due_date": "2025-12-31",
            "team_members": [{"name": "Unassigned", "role": "Developer"}]
        }

def generate_completion(prompt: str) -> str:
    """
    Generate text completion using Gemini API.
    
    Args:
        prompt: String containing the prompt
        
    Returns:
        Generated text response
    """
    try:
        model = genai.GenerativeModel(model_name="gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating completion: {e}")
        return f"Error: Could not generate response due to {str(e)}"
