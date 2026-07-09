import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def get_headers():
    headers = {}
    token = os.getenv("API_AUTHORIZATION_TOKEN")
    if token:
        headers["Authorization"] = token
        
    user_agent = os.getenv("USER_AGENT")
    if user_agent:
        headers["User-Agent"] = user_agent
    return headers

def make_request_with_delay(url, headers=None, delay=2):
    """Makes a request after waiting for the specified delay."""
    time.sleep(delay)
    response = requests.get(url, headers=headers or get_headers())
    response.raise_for_status()
    return response.json()

def get_cached_or_fetch(url, cache_file, headers=None, delay=2):
    """Fetches data from a file cache if available, otherwise from the API."""
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            print(f"Loading data from cache: {cache_file}")
            return json.load(f)
            
    print(f"Fetching data from API: {url}")
    data = make_request_with_delay(url, headers=headers, delay=delay)
    
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    return data
