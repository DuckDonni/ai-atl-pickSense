# #NFL

# #IDs from JSON response
# #tournament_id
# #game_id

# #INPORTANT INFO
# #format: json, xml
# #season_type: PRE, REG, PST
# #season_year: 2000-2025
# #nfl_season_week: 01-18
# #draft_year: 2019-2025
# #Daily Change Log - year: 2014-2025
# #Daily Transactions - year: 2002-2025
# #month: 01-12
# #day: 01-31
# #--------------- Schedule ------------------
# #Current Season Schulde 
# /games/current_season/schedule.{format}

# #Current Week Schedule
# /games/current_week/schedule.{format}

# #Season Schedule 
# /games/{season_year}/{season_type}/schedule.{format}

# #Tournament Schedule (!!!!) tournament id needed
# /tournaments/{tournament_id}/schedule.{format}

# #Weekly Schedule 
# /games/{season_year}/{season_type}/{nfl_season_week}/schedule.{format}

# #--------------- Live Game Updates ------------------
# #Game Play-by-Play
# /games/{game_id}/pbp.{format}

# #Game BoxScore
# /games/{game_id}/boxscore.{format}

# #Game Statistics
# /games/{game_id}/statistics.{format}

# #--------------- Roster ------------------
# #Full Team Roster
# /teams/{team_id}/full_roster.{format}

# #Team Profile
# /teams/{team_id}/profile.{format}

# #Game Roster
# /games/{game_id}/roster.{format}

# #Player Profile
# /players/{player_id}/profile.{format}

# #--------------- Playoffs ------------------
# #Tournament List
# /tournaments/{season_year}/{season_type}/schedule.{format}

# #Tournament Schedule
# /tournaments/{tournament_id}/schedule.{format}

# #Tournament Summary
# /tournaments/{tournament_id}/summary.{format}

# #--------------- Draft Day ------------------
# #Draft Summary
# /{draft_year}/draft.{format}

# #Prospects
# /{draft_year}/prospects.{format}

# #Team Draft Summary
# /{draft_year}/teams/{team_id}/draft.{format}

# #Top Prospects
# /{draft_year}/top_prospects.{format}

# #Trades
# /{draft_year}/trades.{format}

# #--------------- Seasonal Statistics ------------------!!!
# #Seasonal Statistics
# /seasons/{season_year}/{season_type}/teams/{team_id}/statistics.{format}

# #--------------- Standings ------------------!!!!
# #Seasons
# /league/seasons.{format}

# #Postgame Standings
# /seasons/{season_year}/{season_type}/standings/season.{format}

# #Daily Change Log
# /league/{year}/{month}/{day}/changes.{format}

# #--------------- others ------------------
# #Daily Transactions
# /league/{year}/{month}/{day}/transactions.{format}

# #Free Agents
# /league/free_agents.{format}

# #League Hierarchy
# /league/hierarchy.{format}

# #Weekly Injuries
# /seasons/{season_year}/{season_type}/{nfl_season_week}/injuries.{format}

# #Weekly Depth Charts
# /seasons/{season_year}/{season_type}/{nfl_season_week}/depth_charts.{format}
# #--------------- Inportant ------------------
# #Teams (possible the ids)
# /league/teams.{format}


