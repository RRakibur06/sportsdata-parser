from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Sport(str, Enum):
    FOOTBALL = "Football"
    CRICKET = "Cricket"

class Team(BaseModel):
    name: str
    id: int
    image: Optional[str] = None
    country: Optional[int] = None

class Market(BaseModel):
    type: int = Field(description="Market type (1=1X2, 2=Handicap, etc.)")
    outcome: int = Field(description="Outcome type")
    odds: float = Field(description="Decimal odds")
    parameter: Optional[float] = None
    is_main: bool = False

class Markets(BaseModel):
    match_result: List[Market] = Field(default_factory=list, description="1X2 odds")
    over_under: List[Market] = Field(default_factory=list, description="Total goals")
    handicap: List[Market] = Field(default_factory=list, description="Asian handicap")
    both_teams_score: List[Market] = Field(default_factory=list, description="BTTS")
    correct_score: List[Market] = Field(default_factory=list, description="Correct score")

class Weather(BaseModel):
    temperature: Optional[str] = None
    condition: Optional[str] = None
    humidity: Optional[str] = None
    wind_speed: Optional[str] = None
    pressure: Optional[str] = None
    precipitation: Optional[str] = None

class WinProbabilities(BaseModel):
    home_win: Optional[float] = Field(None, alias="P1")
    draw: Optional[float] = Field(None, alias="PX")
    away_win: Optional[float] = Field(None, alias="P2")

class Match(BaseModel):
    id: int
    name: str
    sport: str
    league: str
    country: str
    start_time: datetime
    home_team: Team
    away_team: Team
    venue: Optional[str] = None
    stage: Optional[str] = None
    probabilities: Optional[WinProbabilities] = None
    markets: Markets
    weather: Optional[Weather] = None
    is_live: bool = False
    event_count: int = 0

class ApiResponse(BaseModel):
    error: str = Field(alias="Error")
    error_code: int = Field(alias="ErrorCode")
    success: bool = Field(alias="Success")
    matches: List[Dict[str, Any]] = Field(alias="Value")

class ParsedResponse(BaseModel):
    total_matches: int
    football_matches: int
    cricket_matches: int
    live_matches: int
    matches: List[Match]
    popular_leagues: List[Dict[str, Any]]