import os
import time
import hashlib
import json
import urllib.request
import urllib.parse
import re
from concurrent.futures import ThreadPoolExecutor

SECRET_KEY = "ekomobil_web_2024_secure_key"
BASE_URL = "https://e-komobil.com/yolcu_bilgilendirme_operations.php"
OUTPUT_DIR = "pers_kocaeli"

def get_headers():
    timestamp = str(int(time.time() * 1000))
    token = hashlib.md5((timestamp + SECRET_KEY).encode()).hexdigest()
    return {
        "X-Security-Token": token,
        "X-Security-Timestamp": timestamp,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

def post_request_html(cmd, payload):
    url = f"{BASE_URL}?cmd={cmd}"
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(url, data=data, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode()
    except Exception as e:
        print(f"Error fetching {cmd} with {payload}: {e}")
        return ""

def fetch_buses_for_route(route_code):
    buses = []
    for direction in [0, 1]:
        html = post_request_html("searchBusesontheRoute", {
            "route_code": route_code, 
            "direction": direction
        })
        if html:
            matches = re.findall(r'<input value="([^"]+)">', html)
            for m in matches:
                # 40.76569+29.951298+41 ALL 666+0
                # Could be separated by '+'
                parts = m.split('+')
                if len(parts) >= 3 and ',' not in m: # ignore busOnStopData which has commas
                    buses.append({
                        "route_code": route_code,
                        "direction": direction,
                        "lat": parts[0],
                        "lon": parts[1],
                        "plate": parts[2],
                        "extra": parts[3] if len(parts) > 3 else ""
                    })
    return buses

def main():
    with open(os.path.join(OUTPUT_DIR, "routes.json"), "r", encoding="utf-8") as f:
        routes = json.load(f)
        
    print(f"Loaded {len(routes)} routes. Fetching live buses...")
    all_buses = []
    
    def fetch_and_store(route):
        route_code = route['route_code']
        buses = fetch_buses_for_route(route_code)
        if buses:
            print(f"Found {len(buses)} buses on route {route_code}")
        return buses

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_and_store, routes)
        for res in results:
            all_buses.extend(res)
            
    print(f"Total live buses found: {len(all_buses)}")
    with open(os.path.join(OUTPUT_DIR, "live_buses.json"), "w", encoding="utf-8") as f:
        json.dump(all_buses, f, ensure_ascii=False, indent=2)
        
    print(f"All data saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
