import os
import json
import requests
from pathlib import Path

from logger import logger

LIVE_JSON_URL = "https://coreytshaffer.github.io/clear-lake-watch/data/live.json"
CACHE_DIR = Path("data/sensors")
CACHE_FILE = CACHE_DIR / "live.json"

class ClearLakeWatchIngestor:
    @staticmethod
    def sync():
        """
        Polls the remote Clear Lake Watch URL for the latest live.json data and caches it locally.
        """
        logger.info(f"Syncing Clear Lake Watch data from {LIVE_JSON_URL}...")
        try:
            response = requests.get(LIVE_JSON_URL, timeout=10)
            response.raise_for_status()
            
            # Ensure the cache directory exists
            os.makedirs(CACHE_DIR, exist_ok=True)
            
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(response.json(), f, indent=4)
                
            logger.info("Successfully synced and cached live.json.")
            return True
        except Exception as e:
            logger.error(f"Failed to sync Clear Lake Watch data: {e}")
            return False

    @staticmethod
    def get_cached_data():
        """
        Retrieves the cached live.json payload from the local disk.
        Returns empty dict if no cache exists.
        """
        if not CACHE_FILE.exists():
            logger.warning("No local sensor cache found. Please run a pre-departure sync.")
            return {}
            
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read cached live.json: {e}")
            return {}
