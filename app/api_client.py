import requests
from typing import Dict, Any, Optional
import json
from datetime import datetime
import httpx

class XBetApiClient:
    def __init__(self, base_url: str = "https://1xbetbd.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    # async def fetch_matches(
    #     self,
    #     count: int = 10,
    #     language: str = "en",
    #     mode: int = 4,
    #     country: int = 19,
    #     top: bool = True,
    #     group: int = 925
    # ) -> Optional[Dict[str, Any]]:
    #     """Fetch matches from 1xbet API"""
        
    #     url = f"{self.base_url}/LineFeed/Get1x2_VZip"
    #     params = {
    #         "count": count,
    #         "lng": language,
    #         "mode": mode,
    #         "country": country,
    #         "top": str(top).lower(),
    #         "gr": group
    #     }
        
        # try:
        #     response = self.session.get(url, params=params, timeout=10)
        #     response.raise_for_status()
        #     return response.json()
        # except requests.exceptions.RequestException as e:
        #     print(f"Error fetching data: {e}")
        #     return None
        # except json.JSONDecodeError as e:
        #     print(f"Error parsing JSON: {e}")
        #     return None

    async def fetch_matches(
        self,
        sports: int = 66,  # default sport ID
        count: int = 50,
        lng: str = "en",
        tf: int = 2200000,
        tz: int = 6,
        mode: int = 4,
        country: int = 19,
        get_empty: bool = True,
        gr: int = 925
    ):
        url = f"{self.base_url}/LineFeed/Get1x2_VZip"
        params = {
            "sports": sports,
            "count": count,
            "lng": lng,
            "tf": tf,
            "tz": tz,
            "mode": mode,
            "country": country,
            "getEmpty": str(get_empty).lower(),
            "gr": gr
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    
    def save_response(self, data: Dict[str, Any], filename: str = None):
        """Save API response to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/api_response_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename