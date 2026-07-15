import urllib.request
import urllib.parse
import time
import hashlib
import json
import re

SECRET_KEY = "ekomobil_web_2024_secure_key"
BASE_URL = "https://e-komobil.com/yolcu_bilgilendirme_operations.php"

def get_auth_headers():
    timestamp = str(int(time.time() * 1000))
    token = hashlib.md5((timestamp + SECRET_KEY).encode()).hexdigest()
    return {
        "X-Security-Token": token,
        "X-Security-Timestamp": timestamp,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

def fetch_json(cmd, params={}, method="GET"):
    url = f"{BASE_URL}?cmd={cmd}"
    if method == "GET" and params:
        url += "&" + urllib.parse.urlencode(params)
    
    headers = get_auth_headers()
    
    if method == "POST":
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(url, data=data, headers=headers)
    else:
        req = urllib.request.Request(url, headers=headers)
        
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode()
            if not res_body.strip(): return None
            try:
                return json.loads(res_body)
            except:
                return res_body # Might be HTML
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_all_routes():
    print("[E-Komobil] Brute-forcing route lists...")
    all_routes = {}
    search_chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    for char in search_chars:
        routes = fetch_json("searchRoute", {"term": char}, method="GET")
        if isinstance(routes, list):
            for r in routes:
                code = r.get("route_code")
                if code and code not in all_routes:
                    all_routes[code] = r
    print(f"[E-Komobil] Found {len(all_routes)} unique bus/minibus routes.")
    return list(all_routes.values())

def get_route_stops(route_code, direction=0):
    html = fetch_json("searchRouteStops", {"route_code": route_code, "direction": direction}, method="GET")
    stops = []
    if html and isinstance(html, str):
        matches = re.findall(r'<input[^>]*type="hidden"[^>]*value="([^"]+)"', html)
        for m in matches:
            parts = m.split('+')
            if len(parts) >= 4:
                stops.append({
                    "stop_id": parts[0],
                    "stop_name": parts[1],
                    "lat": parts[2],
                    "lon": parts[3]
                })
    return stops

def get_route_shape(route_code, direction=0):
    data = fetch_json("searchRouteCoordPoints", {"route_code": route_code, "direction": direction}, method="POST")
    if isinstance(data, list):
        return data # expects list of {lat, lng} or [lat, lng]
    return []

def get_live_buses(route_code):
    buses = []
    for direction in [0, 1]:
        html = fetch_json("searchBusesontheRoute", {"route_code": route_code, "direction": direction}, method="POST")
        if html and isinstance(html, str):
            matches = re.findall(r'<input value="([^"]+)">', html)
            for m in matches:
                parts = m.split('+')
                if len(parts) >= 3 and ',' not in m:
                    buses.append({
                        "route_code": route_code,
                        "direction": direction,
                        "lat": parts[0],
                        "lon": parts[1],
                        "plate": parts[2],
                        "extra": parts[3] if len(parts) > 3 else ""
                    })
    return buses
