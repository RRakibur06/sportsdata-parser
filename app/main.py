from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
import json
import pandas as pd
from datetime import datetime
import os

from .parser import BettingDataParser
from .api_client import XBetApiClient
from .models import Match, ParsedResponse

# Create FastAPI app
app = FastAPI(
    title="1xbet Data Parser API",
    description="Parse and analyze 1xbet betting data",
    version="1.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Global variables
current_parser: Optional[BettingDataParser] = None
api_client = XBetApiClient()

# Load sample data on startup
@app.on_event("startup")
async def startup_event():
    global current_parser
    try:
        # Try to load sample data
        with open("data/sample_data.json", "r", encoding="utf-8") as f:
            sample_data = json.load(f)
        current_parser = BettingDataParser(sample_data)
        print(f"Loaded {len(current_parser.matches)} matches from sample data")
    except FileNotFoundError:
        print("No sample data found. Use /fetch-live to get live data.")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Web dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "has_data": current_parser is not None,
        "total_matches": len(current_parser.matches) if current_parser else 0
    })

@app.get("/api/summary")
async def get_summary():
    """Get data summary"""
    if not current_parser:
        raise HTTPException(status_code=404, detail="No data available")
    
    return {
        "total_matches": len(current_parser.matches),
        "football_matches": len(current_parser.get_football_matches()),
        "cricket_matches": len(current_parser.get_cricket_matches()),
        "live_matches": len(current_parser.get_live_matches()),
        "popular_leagues": current_parser.get_popular_leagues()
    }

@app.get("/api/matches", response_model=List[Match])
async def get_matches(
    sport: Optional[str] = Query(None, description="Filter by sport (football/cricket)"),
    live_only: bool = Query(False, description="Show only live matches"),
    min_odds: Optional[float] = Query(None, description="Minimum odds filter"),
    limit: int = Query(100, description="Maximum number of matches to return")
):
    """Get matches with optional filters"""
    if not current_parser:
        raise HTTPException(status_code=404, detail="No data available")
    
    matches = current_parser.matches
    
    # Apply filters
    if sport:
        matches = [m for m in matches if m.sport.lower() == sport.lower()]
    
    if live_only:
        matches = [m for m in matches if m.is_live]
    
    if min_odds:
        matches = [
            m for m in matches 
            if any(market.odds >= min_odds for market in m.markets.match_result)
        ]
    
    return matches[:limit]

@app.get("/api/match/{match_id}")
async def get_match(match_id: int):
    """Get specific match by ID"""
    if not current_parser:
        raise HTTPException(status_code=404, detail="No data available")
    
    match = next((m for m in current_parser.matches if m.id == match_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    return match

@app.get("/api/leagues")
async def get_leagues():
    """Get all leagues with match counts"""
    if not current_parser:
        raise HTTPException(status_code=404, detail="No data available")
    
    return current_parser.get_popular_leagues()

@app.post("/api/fetch-live")
async def fetch_live_data(
    count: int = Query(100, description="Number of matches to fetch"),
    sports: int = Query(66, description="Sport ID to fetch (e.g., 1 for football, 66 for cricket)")
):
    """Fetch live data from 1xbet API"""
    global current_parser
    
    try:
        data = await api_client.fetch_matches(count=count, sports=sports)
        if not data:
            raise HTTPException(status_code=503, detail="Failed to fetch live data")
        
        # Save the response
        filename = api_client.save_response(data)
        
        # Parse the data
        current_parser = BettingDataParser(data)
        
        return {
            "success": True,
            "matches_fetched": len(current_parser.matches),
            "saved_to": filename,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/api/export/csv")
async def export_csv():
    """Export matches to CSV"""
    if not current_parser:
        raise HTTPException(status_code=404, detail="No data available")
    
    # Convert to DataFrame
    matches_data = []
    for match in current_parser.matches:
        # Get 1X2 odds
        home_odds = next((m.odds for m in match.markets.match_result if m.outcome == 1), None)
        draw_odds = next((m.odds for m in match.markets.match_result if m.outcome == 2), None)
        away_odds = next((m.odds for m in match.markets.match_result if m.outcome == 3), None)
        
        matches_data.append({
            "Match": match.name,
            "Sport": match.sport,
            "League": match.league,
            "Country": match.country,
            "Start Time": match.start_time.isoformat(),
            "Home Team": match.home_team.name,
            "Away Team": match.away_team.name,
            "Home Win Odds": home_odds,
            "Draw Odds": draw_odds,
            "Away Win Odds": away_odds,
            "Venue": match.venue,
            "Is Live": match.is_live
        })
    
    df = pd.DataFrame(matches_data)
    filename = f"data/matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    
    return FileResponse(
        filename,
        media_type="text/csv",
        filename=f"matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

@app.get("/api/export/json")
async def export_json():
    """Export matches to JSON"""
    if not current_parser:
        raise HTTPException(status_code=404, detail="No data available")
    
    filename = f"data/matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(current_parser.to_dict(), f, indent=2, default=str)
    
    return FileResponse(
        filename,
        media_type="application/json",
        filename=f"matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)