import os
from dotenv import load_dotenv
from scripts.utils import make_request_with_delay
import json

def fetch_live_data():
    load_dotenv()
    
    url = os.getenv("LIVE_API_URL")
    if not url:
        print("LIVE_API_URL not configured")
        return None

    try:
        print(f"Fetching live data from API: {url}")
        data = make_request_with_delay(url)
        
        # Save payload
        os.makedirs("data", exist_ok=True)
        with open("data/raw_live.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print("Successfully fetched and saved live data.")
        return data
    except Exception as e:
        print(f"Error fetching live data: {e}")
        return None

if __name__ == "__main__":
    fetch_live_data()
