import os
import json
import csv
from datetime import datetime

DATA_DIR = "data/raw"
GTFS_DIR = "data/gtfs"
os.makedirs(GTFS_DIR, exist_ok=True)

def build_gtfs():
    print(f"[{datetime.now()}] Building GTFS files from raw JSON data...")
    
    # 1. Load data
    try:
        with open(os.path.join(DATA_DIR, "routes.json"), "r", encoding="utf-8") as f:
            raw_routes = json.load(f)
        with open(os.path.join(DATA_DIR, "stops.json"), "r", encoding="utf-8") as f:
            raw_stops = json.load(f)
        with open(os.path.join(DATA_DIR, "shapes.json"), "r", encoding="utf-8") as f:
            raw_shapes = json.load(f)
    except Exception as e:
        print(f"Error loading raw data. Make sure crawler has run once. {e}")
        return

    # 2. agency.txt
    with open(os.path.join(GTFS_DIR, "agency.txt"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["agency_id", "agency_name", "agency_url", "agency_timezone", "agency_lang"])
        writer.writerow(["kocaeli", "Kocaeli Büyükşehir Belediyesi", "https://e-komobil.com", "Europe/Istanbul", "tr"])

    # 3. calendar.txt
    with open(os.path.join(GTFS_DIR, "calendar.txt"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"])
        writer.writerow(["EVERYDAY", "1", "1", "1", "1", "1", "1", "1", "20240101", "20301231"])

    # File writers
    f_routes = open(os.path.join(GTFS_DIR, "routes.txt"), "w", newline='', encoding="utf-8")
    f_stops = open(os.path.join(GTFS_DIR, "stops.txt"), "w", newline='', encoding="utf-8")
    f_trips = open(os.path.join(GTFS_DIR, "trips.txt"), "w", newline='', encoding="utf-8")
    f_st = open(os.path.join(GTFS_DIR, "stop_times.txt"), "w", newline='', encoding="utf-8")
    f_shapes = open(os.path.join(GTFS_DIR, "shapes.txt"), "w", newline='', encoding="utf-8")

    r_writer = csv.writer(f_routes)
    s_writer = csv.writer(f_stops)
    t_writer = csv.writer(f_trips)
    st_writer = csv.writer(f_st)
    sh_writer = csv.writer(f_shapes)

    # Headers
    r_writer.writerow(["route_id", "agency_id", "route_short_name", "route_long_name", "route_type"])
    s_writer.writerow(["stop_id", "stop_name", "stop_lat", "stop_lon"])
    t_writer.writerow(["route_id", "service_id", "trip_id", "shape_id", "direction_id"])
    st_writer.writerow(["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"])
    sh_writer.writerow(["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"])

    seen_stops = set()
    
    print(f"[{datetime.now()}] Processing {len(raw_routes)} routes for GTFS export...")
    
    for r in raw_routes:
        route_id = r.get("route_code")
        route_name = r.get("label", "")
        # Standard bus route type is 3
        r_writer.writerow([route_id, "kocaeli", route_id, route_name, 3])
        
        # Directions
        for direction in ["0", "1"]:
            dir_stops = raw_stops.get(route_id, {}).get(direction, [])
            dir_shape = raw_shapes.get(route_id, {}).get(direction, [])
            
            if not dir_stops:
                continue
                
            shape_id = f"shape_{route_id}_{direction}"
            trip_id = f"trip_{route_id}_{direction}"
            
            # Trips
            t_writer.writerow([route_id, "EVERYDAY", trip_id, shape_id, direction])
            
            # Stop Times
            for seq, stop in enumerate(dir_stops):
                stop_id = stop["stop_id"]
                # Default mock time since we don't have static schedules yet for buses
                # Normally GTFS requires arrival/departure times. We use a dummy for now.
                hour = 8 + (seq * 5) // 60
                minute = (seq * 5) % 60
                time_str = f"{hour:02d}:{minute:02d}:00"
                st_writer.writerow([trip_id, time_str, time_str, stop_id, seq + 1])
                
                # Stops
                if stop_id not in seen_stops:
                    s_writer.writerow([stop_id, stop["stop_name"], stop["lat"], stop["lon"]])
                    seen_stops.add(stop_id)
                    
            # Shapes for Buses
            for seq, pt in enumerate(dir_shape):
                lat = pt.get("lat")
                lon = pt.get("lng")
                if lat and lon:
                    sh_writer.writerow([shape_id, lat, lon, seq + 1])

    try:
        with open(os.path.join(DATA_DIR, "trams.json"), "r", encoding="utf-8") as f:
            raw_trams = json.load(f)
            
        print(f"[{datetime.now()}] Processing Akçaray Trams for GTFS export...")
        if raw_trams and raw_trams.get("status") == "ok":
            tram_routes = raw_trams.get("routes", {})
            for route_id, data in tram_routes.items():
                r_writer.writerow([route_id, "kocaeli", route_id, "Akçaray Tramvay", 0]) # route_type 0 is Tram
                
                duraklar = data.get("duraklar", [])
                saatler = data.get("saatler", [])
                
                if duraklar:
                    # Separate directions for stops: "G" (Gidiş) and "D" (Dönüş)
                    gidis_stops = [d for d in duraklar if d.get("yon") == "G"]
                    donus_stops = [d for d in duraklar if d.get("yon") == "D"]
                    
                    for direction, stops_list in [("0", gidis_stops), ("1", donus_stops)]:
                        if not stops_list: continue
                        
                        shape_id = f"shape_{route_id}_{direction}"
                        trip_id = f"trip_{route_id}_{direction}"
                        t_writer.writerow([route_id, "EVERYDAY", trip_id, shape_id, direction])
                        
                        for seq, stop in enumerate(stops_list):
                            stop_id = "TRAM_" + stop.get("durak_kodu", f"unk_{seq}")
                            lat = stop.get("x_koordinat")
                            lon = stop.get("y_koordinat")
                            
                            if stop_id not in seen_stops:
                                s_writer.writerow([stop_id, stop.get("ad", ""), lat, lon])
                                seen_stops.add(stop_id)
                                
                            # Timetable logic for Trams (GidisI, DonusI) could be parsed from 'saatler'
                            # For simplicity, using dummy times for now
                            hour = 8 + (seq * 3) // 60
                            minute = (seq * 3) % 60
                            time_str = f"{hour:02d}:{minute:02d}:00"
                            st_writer.writerow([trip_id, time_str, time_str, stop_id, seq + 1])
                            
                            # Add shape point (Tram doesn't provide explicit shapes, using stop coords)
                            if lat and lon:
                                sh_writer.writerow([shape_id, lat, lon, seq + 1])
    except Exception as e:
        print(f"[{datetime.now()}] Warning: Could not process trams.json: {e}")

    f_routes.close()
    f_stops.close()
    f_trips.close()
    f_st.close()
    f_shapes.close()
    
    # Zip it
    os.system(f"cd {GTFS_DIR} && zip -q gtfs.zip agency.txt calendar.txt routes.txt stops.txt trips.txt stop_times.txt shapes.txt")
    print(f"[{datetime.now()}] GTFS export completed successfully: data/gtfs/gtfs.zip")

if __name__ == "__main__":
    build_gtfs()
