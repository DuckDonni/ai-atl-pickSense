from fastapi import FastAPI
from routes import teams, players
from ai_agent.router import route_query

app = FastAPI()

app.include_router(teams.router, prefix="/teams")
app.include_router(players.router, prefix="/players")

@app.post("/ask")
async def ask_ai(query: str):
    return await route_query(query)
