"""
Configuration module for loading environment variables.
"""
import os

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    # Environment variables can still be set directly in the system
    pass

# Sportradar API Configuration
SPORTRADAR_API_KEY = os.getenv("SPORTRADAR_API_KEY")
SPORTRADAR_BASE_URL = os.getenv("SPORTRADAR_BASE_URL", "https://api.sportradar.com/nfl/official/trial/v7/en")

# Google Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate required environment variables
if not SPORTRADAR_API_KEY:
    raise ValueError(
        "SPORTRADAR_API_KEY environment variable is required. "
        "Please set it in your .env file or as an environment variable. "
        "See backend/README_ENV.md for setup instructions."
    )

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable is required. "
        "Please set it in your .env file or as an environment variable. "
        "See backend/README_ENV.md for setup instructions."
    )

