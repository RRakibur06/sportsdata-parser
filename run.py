import uvicorn
import json
import os
from pathlib import Path

def setup_project():
    """Create necessary directories and files"""
    
    # Create directories
    directories = ["data", "app", "app/templates"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    sample_data_path = "data/sample_data.json"
    if not os.path.exists(sample_data_path):
        print("Creating sample data file...")
        
        sample_data = {
            "Error": "",
            "ErrorCode": 0,
            "Success": True,
            "Value": []  
        }
        
        with open(sample_data_path, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        print(f"Sample data created at {sample_data_path}")
        print("Please update this file with your actual API response data.")
    
    template_path = "app/templates/dashboard.html"
    if not os.path.exists(template_path):
        print("Creating dashboard template...")
        print(f"Dashboard template created at {template_path}")
    
    print("Project setup complete!")

def run_server():
    """Run the FastAPI server"""
    print("Starting FastAPI server...")
    print("Dashboard will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    )

if __name__ == "__main__":
    setup_project()
    run_server()


# Alternative: Simple data analysis script
def analyze_sample_data():
    """Simple analysis without FastAPI"""
    import sys
    sys.path.append('.')
    
    try:
        from app.parser import BettingDataParser
        
        # Load sample data
        with open("data/sample_data.json", 'r', encoding="utf-8") as f:
            data = json.load(f)
        
        # Parse data
        parser = BettingDataParser(data)
        
        print("=== 1XBET DATA ANALYSIS ===\n")
        print(f"Total Matches: {len(parser.matches)}")
        print(f"Football Matches: {len(parser.get_football_matches())}")
        print(f"Cricket Matches: {len(parser.get_cricket_matches())}")
        print(f"Live Matches: {len(parser.get_live_matches())}")
        
        print("\n=== POPULAR LEAGUES ===")
        for league in parser.get_popular_leagues()[:5]:
            print(f"{league['league']}: {league['count']} matches")
        
        if parser.matches:
            match = parser.matches[0]
            print(f"\n=== SAMPLE MATCH ===")
            print(f"Name: {match.name}")
            print(f"League: {match.league}")
            print(f"Teams: {match.home_team.name} vs {match.away_team.name}")
            print(f"Start: {match.start_time}")
            
            if match.markets.match_result:
                print("\n1X2 Odds:")
                for market in match.markets.match_result:
                    outcome = "Home" if market.outcome == 1 else "Draw" if market.outcome == 2 else "Away"
                    print(f"  {outcome}: {market.odds}")
        
        # Export to CSV
        import pandas as pd
        matches_data = []
        for match in parser.matches:
            home_odds = next((m.odds for m in match.markets.match_result if m.outcome == 1), None)
            draw_odds = next((m.odds for m in match.markets.match_result if m.outcome == 2), None)
            away_odds = next((m.odds for m in match.markets.match_result if m.outcome == 3), None)
            
            matches_data.append({
                "Match": match.name,
                "Sport": match.sport,
                "League": match.league,
                "Home Team": match.home_team.name,
                "Away Team": match.away_team.name,
                "Home Odds": home_odds,
                "Draw Odds": draw_odds,
                "Away Odds": away_odds,
                "Start Time": match.start_time,
                "Venue": match.venue
            })
        
        df = pd.DataFrame(matches_data)
        df.to_csv("data/analysis_results.csv", index=False)
        
        print(f"\n=== EXPORT ===")
        print(f"Results exported to data/analysis_results.csv")
        print(f"Total rows: {len(df)}")
        
    except FileNotFoundError:
        print("Error: sample_data.json not found!")
        print("Please create data/sample_data.json with your API response.")
    except Exception as e:
        print(f"Error: {e}")

# analyze_sample_data()