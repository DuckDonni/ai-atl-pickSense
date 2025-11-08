# Environment Setup

This project uses environment variables to store API keys securely.

## Setup Instructions

1. **Install python-dotenv** (if not already installed):
   ```bash
   pip install python-dotenv
   ```

2. **Create a `.env` file** in the `backend` directory:
   ```bash
   cd backend
   cp env.example .env
   ```

3. **Edit the `.env` file** and add your API keys:
   ```env
   SPORTRADAR_API_KEY=your_actual_sportradar_api_key_here
   SPORTRADAR_BASE_URL=https://api.sportradar.com/nfl/official/trial/v7/en
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

## Getting API Keys

- **Sportradar API**: Get your key from [https://sportradar.com/api](https://sportradar.com/api)
- **Google Gemini API**: Get your key from [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

## Important Notes

- The `.env` file is already in `.gitignore` and will NOT be committed to version control
- Never commit your actual API keys to the repository
- The `env.example` file is a template that can be safely committed

