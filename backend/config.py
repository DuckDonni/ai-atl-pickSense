"""
Configuration module for loading environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Sportradar API Configuration
SPORTRADAR_API_KEY = os.getenv("SPORTRADAR_API_KEY")
SPORTRADAR_BASE_URL = os.getenv("SPORTRADAR_BASE_URL", "https://api.sportradar.com/nfl/official/trial/v7/en")

# Google Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate required environment variables
if not SPORTRADAR_API_KEY:
    raise ValueError("SPORTRADAR_API_KEY environment variable is required. Please set it in your .env file.")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required. Please set it in your .env file.")

