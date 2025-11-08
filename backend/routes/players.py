from fastapi import APIRouter, Query
import requests
from routes.teams import get_all_teams

"""
NFL API v7 - Player information using Player Profile and Team Roster feeds.
Based on API map: 
- Team Roster feed: /teams/{id}/roster.json
- Player Profile feed: /players/{id}/profile.json
"""

router = APIRouter()
API_KEY = "ofT8UtZNFrpPsYJtOcsAQJYy22T2lL4qTc9ccC89"
BASE_URL = "https://api.sportradar.com/nfl/official/trial/v7/en"

def search_player_in_roster(team_id, player_name):
    """
    Search for a player in a team's roster using Team Roster feed.
    Endpoint: /teams/{team_id}/roster.json
    """
    try:
        roster_url = f"{BASE_URL}/teams/{team_id}/roster.json?api_key={API_KEY}"
        response = requests.get(roster_url, timeout=10)
        
        if response.status_code == 200:
            roster_data = response.json()
            player_name_lower = player_name.lower()
            
            # Try different roster structures
            players = []
            
            # Direct players array
            if "players" in roster_data:
                players = roster_data["players"] if isinstance(roster_data["players"], list) else [roster_data["players"]]
            # Direct player array
            elif "player" in roster_data:
                players = roster_data["player"] if isinstance(roster_data["player"], list) else [roster_data["player"]]
            # Game structure with home/away
            elif "home" in roster_data or "away" in roster_data:
                for side in ["home", "away"]:
                    if side in roster_data:
                        team_data = roster_data[side]
                        team_players = team_data.get("player", team_data.get("players", []))
                        if team_players:
                            players.extend(team_players if isinstance(team_players, list) else [team_players])
            
            # Search for player
            for player in players:
                full_name = player.get("full_name", "")
                first_name = player.get("first_name", "")
                last_name = player.get("last_name", "")
                
                if (player_name_lower in full_name.lower() or
                    player_name_lower == f"{first_name} {last_name}".lower() or
                    player_name_lower == last_name.lower()):
                    return {
                        "player_id": player.get("id"),
                        "player_name": full_name,
                        "position": player.get("position"),
                        "team_id": team_id,
                        "team_name": roster_data.get("name", "")
                    }
    except Exception:
        pass
    
    return None

def get_player_profile(player_id):
    """
    Get player profile using Player Profile feed.
    Endpoint: /players/{player_id}/profile.json
    """
    try:
        profile_url = f"{BASE_URL}/players/{player_id}/profile.json?api_key={API_KEY}"
        response = requests.get(profile_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, dict) and len(data) > 0:
                if "error" not in str(data).lower() and (data.get("id") or data.get("full_name")):
                    return data
    except Exception:
        pass
    
    return None

def find_team_by_name(team_name, teams):
    """Find a team by name (case-insensitive, partial match)."""
    team_name_lower = team_name.lower()
    for team in teams:
        team_display_name = team.get("name", "")
        if team_name_lower in team_display_name.lower():
            return team.get("id")
    return None

@router.get("/info/{player_name}")
def get_player_info(player_name: str, team: str = Query(None, description="Optional team name to search first")):
    """Get player information by searching team rosters."""
    # Normalize player name
    normalized_name = player_name.replace("-", " ").strip()
    
    # Get all teams using Teams feed
    teams = get_all_teams()
    
    if not teams:
        return {"status": "unavailable", "message": "Could not retrieve teams list"}
    
    # If team is specified, search that team first
    if team:
        team_id = find_team_by_name(team, teams)
        if team_id:
            player_info = search_player_in_roster(team_id, normalized_name)
            if player_info:
                # Found in specified team, get profile
                profile = get_player_profile(player_info["player_id"])
                if profile:
                    return profile
                return {
                    "status": "found",
                    "player_info": player_info,
                    "message": "Found player but could not retrieve full profile"
                }
        # If not found in specified team, continue to search all teams
    
    # Search all teams for the player
    for team_obj in teams:
        team_id = team_obj.get("id")
        if not team_id:
            continue
        
        player_info = search_player_in_roster(team_id, normalized_name)
        if player_info:
            # Found player, get their profile
            profile = get_player_profile(player_info["player_id"])
            if profile:
                return profile
            return {
                "status": "found",
                "player_info": player_info,
                "message": "Found player but could not retrieve full profile"
            }
    
    # Player not found in any team
    return {"status": "unavailable"}
