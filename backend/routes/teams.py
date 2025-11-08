from fastapi import APIRouter
import requests

router = APIRouter()
API_KEY = "ofT8UtZNFrpPsYJtOcsAQJYy22T2lL4qTc9ccC89"
BASE_URL = "https://api.sportradar.com/nfl/official/trial/v7/en"

@router.get("/schedule/{team_name}")
def get_team_schedule(team_name: str):
    # Example simplified logic
    url = f"{BASE_URL}/games/2025/REG/schedule.json?api_key={API_KEY}"
    data = requests.get(url).json()
    # find games matching team_name
    results = []
    for week in data.get("weeks", []):
        for game in week.get("games", []):
            if team_name.lower() in (
                game.get("home", {}).get("name", "").lower(),
                game.get("away", {}).get("name", "").lower(),
            ):
                results.append({
                    "week": week["sequence"],
                    "home": game["home"]["name"],
                    "away": game["away"]["name"],
                    "time": game["scheduled"]
                })
    return {"games": results[:5]}
