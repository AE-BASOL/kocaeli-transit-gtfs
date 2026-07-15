import os
import json
import time
from datetime import datetime
from ekomobil import get_all_routes, get_route_stops, get_route_shape, get_live_buses
from web_scraper import scrape_akcaray_schedule, scrape_ferry_schedule
from classifier import classify_vehicle

DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def update_static_data(force=False):
    """Fetches all routes, stops, and shapes (Runs occasionally, e.g., daily)"""
    if not force and os.path.exists(os.path.join(RAW_DIR, "shapes.json")):
        print(f"[{datetime.now()}] STATIC data already exists. Skipping.")
        return

    print(f"[{datetime.now()}] Starting STATIC data update...")
    routes = get_all_routes()
    
    with open(os.path.join(RAW_DIR, "routes.json"), "w", encoding="utf-8") as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)
        
    all_stops = {}
    all_shapes = {}
    
    print(f"[{datetime.now()}] Fetching stops and shapes for {len(routes)} routes...")
    for i, r in enumerate(routes):
        code = r.get("route_code")
        
        # We fetch direction 0 and 1
        stops_d0 = get_route_stops(code, 0)
        stops_d1 = get_route_stops(code, 1)
        all_stops[code] = {"0": stops_d0, "1": stops_d1}
        
        shape_d0 = get_route_shape(code, 0)
        shape_d1 = get_route_shape(code, 1)
        all_shapes[code] = {"0": shape_d0, "1": shape_d1}
        
        if (i+1) % 10 == 0:
            print(f"[{datetime.now()}] Processed {i+1}/{len(routes)} routes...")
            time.sleep(1) # Be nice to the server
            
    with open(os.path.join(RAW_DIR, "stops.json"), "w", encoding="utf-8") as f:
        json.dump(all_stops, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(RAW_DIR, "shapes.json"), "w", encoding="utf-8") as f:
        json.dump(all_shapes, f, ensure_ascii=False, indent=2)
        
    print(f"[{datetime.now()}] STATIC data update complete.")
    
    print(f"[{datetime.now()}] Fetching Tram & Ferry schedules...")
    trams = scrape_akcaray_schedule()
    ferries = scrape_ferry_schedule()
    
    with open(os.path.join(RAW_DIR, "trams.json"), "w", encoding="utf-8") as f:
        json.dump(trams, f, ensure_ascii=False, indent=2)
    with open(os.path.join(RAW_DIR, "ferries.json"), "w", encoding="utf-8") as f:
        json.dump(ferries, f, ensure_ascii=False, indent=2)

from concurrent.futures import ThreadPoolExecutor

def update_live_data():
    """Fetches live bus locations (Runs continuously)"""
    try:
        with open(os.path.join(RAW_DIR, "routes.json"), "r", encoding="utf-8") as f:
            routes = json.load(f)
    except FileNotFoundError:
        print("Routes not found. Run static update first.")
        return
        
    print(f"[{datetime.now()}] Fetching LIVE data for {len(routes)} routes (Parallel)...")
    all_live_buses = []
    
    def fetch_route(route):
        return get_live_buses(route.get("route_code"))

    with ThreadPoolExecutor(max_workers=15) as executor:
        results = executor.map(fetch_route, routes)
        for res in results:
            if res:
                all_live_buses.extend([classify_vehicle(bus) for bus in res])
        
    with open(os.path.join(PROCESSED_DIR, "live_buses.json"), "w", encoding="utf-8") as f:
        json.dump(all_live_buses, f, ensure_ascii=False, indent=2)
        
    print(f"[{datetime.now()}] LIVE data update complete. Found {len(all_live_buses)} active buses.")
    
    # 4. Phase: Generate GTFS-RT
    try:
        from src.gtfs.rt_builder import build_rt_feed
        build_rt_feed()
    except Exception as e:
        print(f"[{datetime.now()}] Warning: Could not build GTFS-RT: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--static":
        update_static_data()
    elif len(sys.argv) > 1 and sys.argv[1] == "--live":
        update_live_data()
    else:
        # Continuous flow mode
        print("Starting continuous crawler loop...")
        last_static_update = 0
        STATIC_UPDATE_INTERVAL = 86400 # 24 hours
        LIVE_UPDATE_INTERVAL = 60 # 60 seconds
        
        while True:
            current_time = time.time()
            if current_time - last_static_update > STATIC_UPDATE_INTERVAL:
                update_static_data()
                last_static_update = current_time
                
            update_live_data()
            print(f"Sleeping for {LIVE_UPDATE_INTERVAL} seconds...")
            time.sleep(LIVE_UPDATE_INTERVAL)
