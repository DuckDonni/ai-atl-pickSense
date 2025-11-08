import requests
import pandas as pd
from datetime import datetime, timezone
from config import SPORTRADAR_API_KEY, SPORTRADAR_BASE_URL

API_KEY = SPORTRADAR_API_KEY
BASE_URL = SPORTRADAR_BASE_URL

def get_upcoming_games(season_year=2025, season_type="REG", limit=10):
    url = f"{BASE_URL}/games/{season_year}/{season_type}/schedule.json?api_key={API_KEY}"
    print(f"Requesting: {url}")

    response = requests.get(url)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None

    data = response.json()
    games = []

    # current time in UTC
    now = datetime.now(timezone.utc)

    # flatten and filter future games
    for week in data.get("weeks", []):
        for game in week.get("games", []):
            try:
                game_time = datetime.fromisoformat(game["scheduled"].replace("Z", "+00:00"))
                if game_time > now:
                    games.append({
                        "week": week.get("sequence"),
                        "home": game.get("home", {}).get("name"),
                        "away": game.get("away", {}).get("name"),
                        "scheduled": game_time,
                        "venue": game.get("venue", {}).get("name", "Unknown")
                    })
            except Exception:
                continue

    # sort by time and get next 10
    games.sort(key=lambda g: g["scheduled"])
    upcoming = games[:limit]

    df = pd.DataFrame(upcoming)
    print("\n🏈 Next Scheduled NFL Games:")
    print(df.to_string(index=False))

    return df

if __name__ == "__main__":
    get_upcoming_games(2025, "REG", 10)
