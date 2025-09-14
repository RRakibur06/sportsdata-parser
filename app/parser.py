import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from .models import Match, Team, Market, Markets, Weather, WinProbabilities, ApiResponse

class BettingDataParser:
    def __init__(self, api_response: Dict[str, Any]):
        self.raw_data = api_response
        self.matches = self._parse_matches()
    
    def _parse_matches(self) -> List[Match]:
        """Parse raw API response into structured matches"""
        matches = []
        
        for match_data in self.raw_data.get("Value", []):
            try:
                parsed_match = self._parse_single_match(match_data)
                matches.append(parsed_match)
            except Exception as e:
                print(f"Error parsing match {match_data.get('I', 'unknown')}: {e}")
                continue
        
        return matches
    
    def _parse_single_match(self, match_data: Dict[str, Any]) -> Match:
        """Parse a single match from raw data"""
        
        # Basic match info
        match_id = match_data.get("I")
        name = match_data.get("L", "")
        sport = match_data.get("SE", "")
        league = match_data.get("LE", "")
        country = match_data.get("CN", "")
        start_timestamp = match_data.get("S", 0)
        start_time = datetime.fromtimestamp(start_timestamp) if start_timestamp else datetime.now()
        
        # Teams
        home_team = Team(
            name=match_data.get("O1", ""),
            id=match_data.get("O1I", 0),
            image=match_data.get("O1IMG", [None])[0] if match_data.get("O1IMG") else None,
            country=match_data.get("O1C")
        )
        
        away_team = Team(
            name=match_data.get("O2", ""),
            id=match_data.get("O2I", 0),
            image=match_data.get("O2IMG", [None])[0] if match_data.get("O2IMG") else None,
            country=match_data.get("O2C")
        )
        
        # Venue and stage
        venue_info = match_data.get("MIO", {})
        venue = venue_info.get("Loc") if venue_info else None
        stage = venue_info.get("TSt") if venue_info else None
        
        # Win probabilities
        wp_data = match_data.get("WP", {})
        probabilities = WinProbabilities(
            home_win=wp_data.get("P1"),
            draw=wp_data.get("PX"),
            away_win=wp_data.get("P2")
        ) if wp_data else None
        
        # Markets
        markets = self._parse_markets(
            match_data.get("E", []),
            match_data.get("AE", [])
        )
        
        # Weather
        weather = self._parse_weather(match_data.get("MIS", []))
        
        # Status
        is_live = match_data.get("SS", 0) == 1
        event_count = match_data.get("EC", 0)
        
        return Match(
            id=match_id,
            name=name,
            sport=sport,
            league=league,
            country=country,
            start_time=start_time,
            home_team=home_team,
            away_team=away_team,
            venue=venue,
            stage=stage,
            probabilities=probabilities,
            markets=markets,
            weather=weather,
            is_live=is_live,
            event_count=event_count
        )
    
    def _parse_markets(self, main_markets: List[Dict], additional_markets: List[Dict]) -> Markets:
        """Parse betting markets"""
        markets = Markets()
        
        # Parse main markets
        for market_data in main_markets:
            market = Market(
                type=market_data.get("G", 0),
                outcome=market_data.get("T", 0),
                odds=market_data.get("C", 0.0),
                parameter=market_data.get("P"),
                is_main=market_data.get("CE") == 1
            )
            
            # Categorize market
            self._categorize_market(market, markets)
        
        # Parse additional markets
        for market_group in additional_markets:
            for market_data in market_group.get("ME", []):
                market = Market(
                    type=market_group.get("G", 0),
                    outcome=market_data.get("T", 0),
                    odds=market_data.get("C", 0.0),
                    parameter=market_data.get("P"),
                    is_main=False
                )
                self._categorize_market(market, markets)
        
        return markets
    
    def _categorize_market(self, market: Market, markets: Markets):
        """Categorize market into appropriate list"""
        market_type = market.type
        
        if market_type == 1:  # 1X2
            markets.match_result.append(market)
        elif market_type in [15, 62]:  # Over/Under
            markets.over_under.append(market)
        elif market_type in [2, 17]:  # Handicap
            markets.handicap.append(market)
        elif market_type == 19:  # Both teams to score
            markets.both_teams_score.append(market)
        elif market_type == 8:  # Correct score
            markets.correct_score.append(market)
    
    def _parse_weather(self, weather_data: List[Dict]) -> Optional[Weather]:
        """Parse weather information"""
        if not weather_data:
            return None
        
        weather_map = {}
        for item in weather_data:
            key = item.get("K")
            value = item.get("V")
            
            if key == 9:
                weather_map["temperature"] = value
            elif key == 21:
                weather_map["condition"] = value
            elif key == 27:
                weather_map["humidity"] = value
            elif key == 23:
                weather_map["wind_speed"] = value
            elif key == 25:
                weather_map["pressure"] = value
            elif key == 35:
                weather_map["precipitation"] = value
        
        return Weather(**weather_map) if weather_map else None
    
    def get_football_matches(self) -> List[Match]:
        """Get only football matches"""
        return [m for m in self.matches if m.sport.lower() == "football"]
    
    def get_cricket_matches(self) -> List[Match]:
        """Get only cricket matches"""
        return [m for m in self.matches if m.sport.lower() == "cricket"]
    
    def get_live_matches(self) -> List[Match]:
        """Get only live matches"""
        return [m for m in self.matches if m.is_live]
    
    def get_matches_with_good_odds(self, min_odds: float = 2.0) -> List[Match]:
        """Get matches with odds above threshold"""
        return [
            m for m in self.matches 
            if any(market.odds >= min_odds for market in m.markets.match_result)
        ]
    
    def get_popular_leagues(self) -> List[Dict[str, Any]]:
        """Get leagues sorted by match count"""
        league_counts = {}
        for match in self.matches:
            league_counts[match.league] = league_counts.get(match.league, 0) + 1
        
        return [
            {"league": league, "count": count}
            for league, count in sorted(league_counts.items(), key=lambda x: x[1], reverse=True)
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parsed data to dictionary"""
        return {
            "total_matches": len(self.matches),
            "football_matches": len(self.get_football_matches()),
            "cricket_matches": len(self.get_cricket_matches()),
            "live_matches": len(self.get_live_matches()),
            "matches": [match.model_dump() for match in self.matches],
            "popular_leagues": self.get_popular_leagues()
        }