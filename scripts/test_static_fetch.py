import os
from dotenv import load_dotenv
from scripts.utils import get_cached_or_fetch

def fetch_static_data():
    load_dotenv()
    
    url = os.getenv("STATIC_API_URL")
    if not url:
        print("STATIC_API_URL not configured")
        return None

    try:
        data = get_cached_or_fetch(url, "data/raw_static.json")
        print("Successfully retrieved static data.")
        return data
    except Exception as e:
        print(f"Error fetching static data: {e}")
        return None

if __name__ == "__main__":
    fetch_static_data()
