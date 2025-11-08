import google.generativeai as genai
import requests
import json
import re

genai.configure(api_key="AIzaSyBEMwJNKQrZbkpvGGKL-4wng0qDO_dAsQU")

FUNCTIONS = {
    "get_team_schedule": {
        "description": "Get a team's upcoming or past games",
        "endpoint": "http://localhost:8000/teams/schedule/{team_name}"
    },
    "get_player_info": {
        "description": "Fetch information about an NFL player by name",
        "endpoint": "http://localhost:8000/players/info/{player_name}"
    }
}

async def route_query(user_input: str):
    # Step 1: Ask Gemini which function matches the query
    prompt = f"""
    You are a routing agent for a sports app.
    Given a user request, pick the best function from the list:
    {list(FUNCTIONS.keys())}

    User request: "{user_input}"
    Respond ONLY with the function name and the parameters (JSON).
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    text = response.text.strip()

    # Step 2: Parse the JSON response
    try:
        # Extract JSON from markdown code blocks if present
        json_text = text
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', json_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            # Try to find JSON object in the text
            json_match = re.search(r'\{.*\}', json_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
        
        # Parse the JSON
        parsed = json.loads(json_text)
        function_name = parsed.get("function_name", "")
        params = parsed.get("parameters", {})
        
        # Determine route and build endpoint
        if function_name == "get_team_schedule" or "team" in function_name.lower():
            team_name = params.get("team_name", params.get("team", "unknown"))
            # Convert team name to URL-friendly format (lowercase, replace spaces with hyphens)
            team_name = team_name.lower().replace(" ", "-")
            endpoint = FUNCTIONS["get_team_schedule"]["endpoint"].format(team_name=team_name)
        elif function_name == "get_player_info" or "player" in function_name.lower():
            player_name = params.get("player_name", params.get("player", "unknown"))
            # Convert player name to URL-friendly format (lowercase, replace spaces with hyphens)
            player_name = player_name.lower().replace(" ", "-")
            endpoint = FUNCTIONS["get_player_info"]["endpoint"].format(player_name=player_name)
        else:
            return {"error": "Unknown route", "gemini_response": text, "parsed": parsed}
            
    except json.JSONDecodeError:
        # Fallback to simple text matching if JSON parsing fails
        if "team" in text.lower() or "get_team_schedule" in text.lower():
            # Try to extract team name from text
            team_match = re.search(r'(?:team|schedule).*?(\w+(?:\s+\w+)*)', text, re.IGNORECASE)
            team_name = team_match.group(1).lower().replace(" ", "-") if team_match else "unknown"
            endpoint = FUNCTIONS["get_team_schedule"]["endpoint"].format(team_name=team_name)
        elif "player" in text.lower() or "get_player_info" in text.lower():
            # Try to extract player name from text
            player_match = re.search(r'(?:player|info).*?(\w+(?:\s+\w+)*)', text, re.IGNORECASE)
            player_name = player_match.group(1).lower().replace(" ", "-") if player_match else "unknown"
            endpoint = FUNCTIONS["get_player_info"]["endpoint"].format(player_name=player_name)
        else:
            return {"error": "Unknown route", "gemini_response": text}

    # Step 3: Call the endpoint and return
    api_response = requests.get(endpoint)
    return api_response.json()
