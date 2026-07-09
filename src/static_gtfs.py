import pandas as pd
import zipfile
import os
import json

def generate_static_gtfs(routes_data, output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    
    agency_df = pd.DataFrame([{
        "agency_id": "kocaeli_buyuksehir",
        "agency_name": "Kocaeli Büyükşehir Belediyesi",
        "agency_url": "https://www.e-komobil.com/",
        "agency_timezone": "Europe/Istanbul",
        "agency_lang": "tr"
    }])
    
    # We must provide minimal stops, trips, etc. for a valid GTFS
    # Since we only have routes, we generate one dummy stop per route or a single central stop
    stops_df = pd.DataFrame([{
        "stop_id": "stop_1",
        "stop_name": "Kocaeli Merkezi (Dummy)",
        "stop_lat": 40.7654,
        "stop_lon": 29.9408
    }])
    
    routes_list = []
    trips_list = []
    stop_times_list = []
    
    for i, r in enumerate(routes_data):
        route_id = r.get("route_code")
        route_name = r.get("label", route_id)
        
        routes_list.append({
            "route_id": route_id,
            "agency_id": "kocaeli_buyuksehir",
            "route_short_name": route_id,
            "route_long_name": route_name,
            "route_type": 3 # Bus
        })
        
        trip_id = f"trip_{route_id}"
        trips_list.append({
            "route_id": route_id,
            "service_id": "service_1",
            "trip_id": trip_id,
            "trip_headsign": route_name
        })
        
        stop_times_list.append({
            "trip_id": trip_id,
            "arrival_time": "08:00:00",
            "departure_time": "08:00:00",
            "stop_id": "stop_1",
            "stop_sequence": 1
        })
        
    if not routes_list:
        routes_list.append({
            "route_id": "route_1",
            "agency_id": "kocaeli_buyuksehir",
            "route_short_name": "11",
            "route_long_name": "Izmit - Umuttepe",
            "route_type": 3
        })
        
    routes_df = pd.DataFrame(routes_list)
    trips_df = pd.DataFrame(trips_list)
    stop_times_df = pd.DataFrame(stop_times_list)
    
    calendar_df = pd.DataFrame([{
        "service_id": "service_1",
        "monday": 1,
        "tuesday": 1,
        "wednesday": 1,
        "thursday": 1,
        "friday": 1,
        "saturday": 1,
        "sunday": 1,
        "start_date": "20240101",
        "end_date": "20301231"
    }])
    
    csv_files = {
        "agency.txt": agency_df,
        "stops.txt": stops_df,
        "routes.txt": routes_df,
        "trips.txt": trips_df,
        "stop_times.txt": stop_times_df,
        "calendar.txt": calendar_df
    }
    
    zip_path = os.path.join(output_dir, "gtfs.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for filename, df in csv_files.items():
            csv_path = os.path.join(output_dir, filename)
            df.to_csv(csv_path, index=False)
            zf.write(csv_path, filename)
            os.remove(csv_path)
            
    return zip_path

if __name__ == "__main__":
    input_file = "pers_kocaeli/routes.json"
    output_dir = "data"
    
    if os.path.exists(input_file):
        with open(input_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    else:
        print(f"Warning: {input_file} not found, generating mock data anyway.")
        raw_data = []
        
    result_path = generate_static_gtfs(raw_data, output_dir=output_dir)
    print(f"Static GTFS generated at: {result_path}")
