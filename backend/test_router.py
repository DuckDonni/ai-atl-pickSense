"""
Test script for the AI router.
Run this script to test sample queries through the console.

Make sure your FastAPI server is running (uvicorn app:app --reload)
before testing queries that need to call endpoints.
"""
import asyncio
import sys
import json
import re
import google.generativeai as genai
import requests

# Configure Gemini (same as router.py)
genai.configure(api_key="AIzaSyBEMwJNKQrZbkpvGGKL-4wng0qDO_dAsQU")

FUNCTIONS = {
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

def print_separator():
    print("\n" + "="*60 + "\n")

async def test_query(query: str, show_gemini_only: bool = False):
    """Test a single query and display the result."""
    print_separator()
    print(f"📝 Query: {query}")
    print("\n🔄 Processing with Gemini...")
    
    try:
        # Step 1: Ask Gemini which function matches the query
        prompt = f"""
        You are a routing agent for a sports app.
        Given a user request, pick the best function from the list:
        {list(FUNCTIONS.keys())}

        User request: "{query}"
        Respond ONLY with the function name and the parameters (JSON).
        If the user mentions a team name along with a player name, include it in the parameters as "team_name".
        """
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        gemini_text = response.text.strip()
        
        print(f"\n🤖 Gemini Response:")
        print(f"   {gemini_text}")
        
        # Step 2: Parse the JSON response
        selected_route = None
        endpoint = None
        params = {}
        
        try:
            # Try to parse function call format: get_player_info({"player_name": "patrick mahomes"})
            # Matches function_name({...}) where function_name can have underscores
            function_call_match = re.search(r'([a-z_]+)\s*\((\{.*?\})\)', gemini_text, re.DOTALL | re.IGNORECASE)
            if function_call_match:
                function_name = function_call_match.group(1)
                params_json = function_call_match.group(2)
                try:
                    params = json.loads(params_json)
                except json.JSONDecodeError:
                    params = {}
            else:
                # Try to parse format without parentheses: get_all_teams{} or get_all_teams
                simple_function_match = re.search(r'([a-z_]+)\s*(\{.*?\})?', gemini_text, re.IGNORECASE)
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
                    json_text = gemini_text
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
                direct_match = re.search(r'\b(get_all_team_names|get_team_schedule|get_player_info)\b', gemini_text, re.IGNORECASE)
                if direct_match:
                    function_name = direct_match.group(1).lower()
            
            # Route all team-related queries (with or without "name") to get_all_team_names
            # This ensures we only return team names, not full team data
            if function_name == "get_all_team_names" or ("all" in function_name.lower() and "team" in function_name.lower()) or function_name == "get_all_teams":
                selected_route = "get_all_team_names"
                endpoint = FUNCTIONS["get_all_team_names"]["endpoint"]
            elif function_name == "get_team_schedule" or ("team" in function_name.lower() and "schedule" in function_name.lower()):
                selected_route = "get_team_schedule"
                team_name = params.get("team_name", params.get("team", "unknown"))
                # Convert team name to URL-friendly format (lowercase, replace spaces with hyphens)
                team_name = team_name.lower().replace(" ", "-")
                endpoint = FUNCTIONS["get_team_schedule"]["endpoint"].format(team_name=team_name)
            elif function_name == "get_player_info" or "player" in function_name.lower():
                selected_route = "get_player_info"
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
                print(f"\n⚠️  Could not determine route from Gemini response")
                print(f"   Function name: {function_name}")
                return {"error": "Unknown route", "gemini_response": gemini_text, "parsed": parsed}
                
        except json.JSONDecodeError as e:
            print(f"\n⚠️  Could not parse JSON from Gemini response")
            print(f"   Error: {e}")
            # Fallback to simple text matching
            # Route all team-related queries to get_all_team_names (only return names, not full data)
            if ("all" in gemini_text.lower() and "team" in gemini_text.lower()) or "get_all_team_names" in gemini_text.lower() or "get_all_teams" in gemini_text.lower():
                selected_route = "get_all_team_names"
                endpoint = FUNCTIONS["get_all_team_names"]["endpoint"]
            elif "team" in gemini_text.lower() and "schedule" in gemini_text.lower():
                selected_route = "get_team_schedule"
                # Try to extract team name from text
                team_match = re.search(r'(?:team|schedule).*?(\w+(?:\s+\w+)*)', gemini_text, re.IGNORECASE)
                team_name = team_match.group(1).lower().replace(" ", "-") if team_match else "unknown"
                endpoint = FUNCTIONS["get_team_schedule"]["endpoint"].format(team_name=team_name)
            elif "player" in gemini_text.lower() or "get_player_info" in gemini_text.lower():
                selected_route = "get_player_info"
                # Try to extract player name from text
                player_match = re.search(r'(?:player|info).*?(\w+(?:\s+\w+)*)', gemini_text, re.IGNORECASE)
                player_name = player_match.group(1).lower().replace(" ", "-") if player_match else "unknown"
                endpoint = FUNCTIONS["get_player_info"]["endpoint"].format(player_name=player_name)
            else:
                print(f"\n⚠️  Could not determine route from Gemini response")
                return {"error": "Unknown route", "gemini_response": gemini_text}
        
        print(f"\n✅ Selected Route: {selected_route}")
        print(f"🔗 Endpoint: {endpoint}")
        
        if show_gemini_only:
            print("\n(Stopping here - Gemini-only mode)")
            return {
                "gemini_response": gemini_text,
                "selected_route": selected_route,
                "endpoint": endpoint
            }
        
        # Step 3: Call the endpoint
        print(f"\n🌐 Calling endpoint...")
        try:
            api_response = requests.get(endpoint, timeout=5)
            result = api_response.json()
            print(f"\n✅ API Response:")
            print(result)
            return result
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Error: Could not connect to API server.")
            print(f"   Make sure FastAPI server is running: uvicorn app:app --reload")
            return {
                "error": "API server not available",
                "gemini_response": gemini_text,
                "selected_route": selected_route,
                "endpoint": endpoint
            }
        except Exception as e:
            print(f"\n❌ Error calling endpoint: {e}")
            return {
                "error": str(e),
                "gemini_response": gemini_text,
                "selected_route": selected_route,
                "endpoint": endpoint
            }
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

async def interactive_mode():
    """Interactive mode - enter queries one by one."""
    print("="*60)
    print("🤖 AI Router Test - Interactive Mode")
    print("="*60)
    print("\nEnter queries to test the routing logic.")
    print("Type 'exit' or 'quit' to stop.")
    print("Type 'gemini-only' to toggle showing only Gemini responses.\n")
    
    gemini_only = False
    
    while True:
        try:
            query = input("Enter your query: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == 'gemini-only':
                gemini_only = not gemini_only
                status = "ON" if gemini_only else "OFF"
                print(f"   Gemini-only mode: {status}\n")
                continue
            
            if not query:
                print("⚠️  Please enter a valid query.\n")
                continue
            
            await test_query(query, show_gemini_only=gemini_only)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

async def batch_mode(queries: list):
    """Test multiple queries in batch."""
    print("="*60)
    print("🤖 AI Router Test - Batch Mode")
    print("="*60)
    
    for i, query in enumerate(queries, 1):
        print(f"\n[Test {i}/{len(queries)}]")
        await test_query(query, show_gemini_only=False)
    
    print_separator()
    print("✅ All tests completed!")

async def main():
    """Main function to run the test script."""
    # Sample test queries
    sample_queries = [
        "get me info on lebrons 3 point average",
        "when do the Chiefs play next?",
        "what's Patrick Mahomes' passing yards?",
        "show me the Cowboys schedule",
        "tell me about Tom Brady's stats",
    ]
    
    show_gemini_only = "--gemini-only" in sys.argv
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--sample":
            # Run sample queries
            await batch_mode(sample_queries)
        elif sys.argv[1] == "--query":
            # Run a single query from command line
            if len(sys.argv) > 2:
                query = " ".join([arg for arg in sys.argv[2:] if arg != "--gemini-only"])
                await test_query(query, show_gemini_only)
            else:
                print("❌ Please provide a query after --query")
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Usage:")
            print("  python test_router.py                    # Interactive mode")
            print("  python test_router.py --sample          # Run sample queries")
            print("  python test_router.py --query 'query'    # Test single query")
            print("  python test_router.py --gemini-only      # Show only Gemini response (no API call)")
            print("\nExamples:")
            print("  python test_router.py --query 'when do the Chiefs play next?'")
            print("  python test_router.py --query 'get me info on lebrons 3 point average' --gemini-only")
        else:
            print("Unknown option. Use --help for usage information.")
    else:
        # Default: interactive mode
        await interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())

