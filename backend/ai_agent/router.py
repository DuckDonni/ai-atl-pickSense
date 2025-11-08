import google.generativeai as genai
import requests
import json
import re

genai.configure(api_key="AIzaSyBEMwJNKQrZbkpvGGKL-4wng0qDO_dAsQU")

FUNCTIONS = {
    # "get_all_teams": {
    #     "description": "Get all teams in the NFL",
    #     "endpoint": "http://localhost:8000/teams/all"
    # },
    "get_all_team_names": {
        "description": "Get a list of all NFL team names",
        "endpoint": "http://localhost:8000/teams/names"
    },
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
    If the user mentions a team name along with a player name, include it in the parameters as "team_name".
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    text = response.text.strip()

    # Step 2: Parse the response (handles multiple formats)
    function_name = ""
    params = {}
    parsed = {}
    
    try:
        # Try to parse function call format: get_player_info({"player_name": "patrick mahomes"})
        # Matches function_name({...}) where function_name can have underscores
        function_call_match = re.search(r'([a-z_]+)\s*\((\{.*?\})\)', text, re.DOTALL | re.IGNORECASE)
        if function_call_match:
            function_name = function_call_match.group(1)
            params_json = function_call_match.group(2)
            try:
                params = json.loads(params_json)
            except json.JSONDecodeError:
                params = {}
        else:
            # Try to parse format without parentheses: get_all_teams{} or get_all_teams
            simple_function_match = re.search(r'([a-z_]+)\s*(\{.*?\})?', text, re.IGNORECASE)
            if simple_function_match:
                function_name = simple_function_match.group(1)
                params_json = simple_function_match.group(2)
                if params_json:
                    try:
                        params = json.loads(params_json)
                    except json.JSONDecodeError:
                        params = {}
                else:
                    params = {}
            else:
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
        if not function_name:
            # If we still don't have a function name, try to extract it directly from text
            direct_match = re.search(r'\b(get_all_team_names|get_team_schedule|get_player_info)\b', text, re.IGNORECASE)
            if direct_match:
                function_name = direct_match.group(1).lower()
        
        # Route all team-related queries (with or without "name") to get_all_team_names
        # This ensures we only return team names, not full team data
        if function_name == "get_all_team_names" or ("all" in function_name.lower() and "team" in function_name.lower()) or function_name == "get_all_teams":
            endpoint = FUNCTIONS["get_all_team_names"]["endpoint"]
        elif function_name == "get_team_schedule" or ("team" in function_name.lower() and "schedule" in function_name.lower()):
            team_name = params.get("team_name", params.get("team", "unknown"))
            # Convert team name to URL-friendly format (lowercase, replace spaces with hyphens)
            team_name = team_name.lower().replace(" ", "-")
            endpoint = FUNCTIONS["get_team_schedule"]["endpoint"].format(team_name=team_name)
        elif function_name == "get_player_info" or "player" in function_name.lower():
            player_name = params.get("player_name", params.get("player", "unknown"))
            # Convert player name to URL-friendly format (lowercase, replace spaces with hyphens)
            player_name = player_name.lower().replace(" ", "-")
            endpoint = FUNCTIONS["get_player_info"]["endpoint"].format(player_name=player_name)
            
            # Check if team is specified in parameters
            team_name = params.get("team_name", params.get("team"))
            if team_name:
                # Add team as query parameter
                from urllib.parse import quote
                team_encoded = quote(team_name)
                endpoint = f"{endpoint}?team={team_encoded}"
        else:
            return {"error": "Unknown route", "gemini_response": text, "parsed": parsed}
            
    except json.JSONDecodeError:
        # Fallback to simple text matching if JSON parsing fails
        # Route all team-related queries to get_all_team_names (only return names, not full data)
        if ("all" in text.lower() and "team" in text.lower()) or "get_all_team_names" in text.lower() or "get_all_teams" in text.lower():
            endpoint = FUNCTIONS["get_all_team_names"]["endpoint"]
        elif "team" in text.lower() and "schedule" in text.lower():
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
