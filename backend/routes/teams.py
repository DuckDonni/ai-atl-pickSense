from fastapi import APIRouter
import requests
from config import SPORTRADAR_API_KEY, SPORTRADAR_BASE_URL

router = APIRouter()
API_KEY = SPORTRADAR_API_KEY
BASE_URL = SPORTRADAR_BASE_URL

def get_all_teams():
    """
    Get list of all NFL teams using the Teams feed.
    Endpoint: /teams.json
    Returns a list of all NFL teams from Sportradar API.
    """
    #/league/teams.{json}
    teams_url = f"{BASE_URL}/league/teams.json?api_key={API_KEY}"
    
    try:
        response = requests.get(teams_url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        if response.status_code == 200:
            data = response.json()
            
            # Debug: Print the structure to understand the response
            print(f"DEBUG: API Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict) and "league" in data:
                print(f"DEBUG: League keys: {list(data['league'].keys()) if isinstance(data['league'], dict) else 'Not a dict'}")
            
            # Based on schema: league -> teams -> team[]
            if isinstance(data, dict):
                # Check for league -> teams -> team[]
                if "league" in data and isinstance(data["league"], dict):
                    league = data["league"]
                    if "teams" in league:
                        teams = league["teams"]
                        if isinstance(teams, dict) and "team" in teams:
                            team_list = teams["team"]
                            # Ensure we return a list
                            if isinstance(team_list, list):
                                print(f"DEBUG: Found {len(team_list)} teams in league.teams.team[]")
                                return team_list
                            elif isinstance(team_list, dict):
                                print(f"DEBUG: Found single team in league.teams.team")
                                return [team_list]
                        elif isinstance(teams, list):
                            print(f"DEBUG: Found {len(teams)} teams in league.teams[]")
                            return teams
                # Check for direct teams -> team[]
                if "teams" in data:
                    teams = data["teams"]
                    if isinstance(teams, dict) and "team" in teams:
                        team_list = teams["team"]
                        if isinstance(team_list, list):
                            print(f"DEBUG: Found {len(team_list)} teams in teams.team[]")
                            return team_list
                        elif isinstance(team_list, dict):
                            print(f"DEBUG: Found single team in teams.team")
                            return [team_list]
                    elif isinstance(teams, list):
                        print(f"DEBUG: Found {len(teams)} teams in teams[]")
                        return teams
                # Check for direct team[]
                if "team" in data:
                    team_list = data["team"]
                    if isinstance(team_list, list):
                        print(f"DEBUG: Found {len(team_list)} teams in team[]")
                        return team_list
                    elif isinstance(team_list, dict):
                        print(f"DEBUG: Found single team in team")
                        return [team_list]
            elif isinstance(data, list):
                print(f"DEBUG: Found {len(data)} teams in root list")
                return data
            
            # If we get here, the structure doesn't match expected patterns
            print(f"DEBUG: Unexpected response structure. Type: {type(data)}")
            if isinstance(data, dict):
                print(f"DEBUG: Top-level keys: {list(data.keys())}")
            return []
                
    except requests.exceptions.RequestException as e:
        print(f"Error fetching teams from Sportradar API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text[:500]}")
    except Exception as e:
        print(f"Unexpected error in get_all_teams: {e}")
        import traceback
        traceback.print_exc()
    
    return []

@router.get("/all")
def get_all_teams_endpoint():
    """
    Get all teams in the NFL.
    Endpoint: GET /teams/all
    Returns all NFL teams from the Teams feed.
    """
    teams = get_all_teams()
    if teams:
        return {
            "status": "success",
            "count": len(teams),
            "teams": teams
        }
    return {
        "status": "unavailable",
        "message": "Could not retrieve teams list"
    }

def get_all_team_names():
    """
    Get a list of all NFL team names.
    Calls get_all_teams() and extracts just the team names.
    Returns a list of team name strings.
    """
    teams = get_all_teams()
    team_names = []
    
    for team in teams:
        if isinstance(team, dict):
            # Try different possible name fields
            name = team.get("name") or team.get("full_name") or team.get("display_name")
            if name:
                team_names.append(name)
    
    return team_names

@router.get("/names")
def get_all_team_names_endpoint():
    """
    Get all NFL team names.
    Endpoint: GET /teams/names
    Returns a list of all NFL team names.
    """
    team_names = get_all_team_names()
    if team_names:
        return {
            "status": "success",
            "count": len(team_names),
            "team_names": team_names
        }
    return {
        "status": "unavailable",
        "message": "Could not retrieve team names"
    }