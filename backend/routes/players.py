from fastapi import APIRouter
import requests

router = APIRouter()
API_KEY = "ofT8UtZNFrpPsYJtOcsAQJYy22T2lL4qTc9ccC89"
BASE_URL = "https://api.sportradar.com/nfl/official/trial/v7/en"

@router.get("/info/{player_name}")
def get_player_info(player_name: str):
    # Placeholder for player info endpoint
    # You'll need to implement the actual Sportradar API call for player stats
    return {
        "player": player_name,
        "message": "Player info endpoint - to be implemented with Sportradar API",
        "note": "This would fetch player statistics from Sportradar"
    }

