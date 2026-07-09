from google.transit import gtfs_realtime_pb2
import time
import os
import json

def generate_rt_gtfs(live_data, output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    feed.header.timestamp = int(time.time())
    
    for idx, bus in enumerate(live_data):
        route_id = bus.get("route_code")
        lat = float(bus.get("lat", 0))
        lon = float(bus.get("lon", 0))
        plate = bus.get("plate", f"bus_{idx}")
        speed = float(bus.get("extra", 0)) if bus.get("extra") else 0.0
        
        # Vehicle Position Entity
        entity = feed.entity.add()
        entity.id = f"vehicle_{plate.replace(' ', '_')}"
        
        trip_id = f"trip_{route_id}"
        
        # Trip Update
        trip_update = entity.trip_update
        trip_update.trip.trip_id = trip_id
        trip_update.trip.route_id = route_id
        
        stop_time_update = trip_update.stop_time_update.add()
        stop_time_update.stop_sequence = 1
        stop_time_update.stop_id = "stop_1"
        stop_time_update.arrival.time = int(time.time()) + 300
        stop_time_update.departure.time = int(time.time()) + 300
        
        # Vehicle Details
        entity.vehicle.trip.trip_id = trip_id
        entity.vehicle.trip.route_id = route_id
        entity.vehicle.position.latitude = lat
        entity.vehicle.position.longitude = lon
        entity.vehicle.position.speed = speed
        entity.vehicle.vehicle.id = plate
        entity.vehicle.current_stop_sequence = 1
        entity.vehicle.stop_id = "stop_1"
        entity.vehicle.timestamp = int(time.time())
        
    output_path = os.path.join(output_dir, "gtfs-rt.pb")
    with open(output_path, "wb") as f:
        f.write(feed.SerializeToString())
        
    return output_path

if __name__ == "__main__":
    input_file = "pers_kocaeli/live_buses.json"
    output_dir = "data"
    
    if os.path.exists(input_file):
        with open(input_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    else:
        print(f"Warning: {input_file} not found, generating empty data.")
        raw_data = []
        
    result_path = generate_rt_gtfs(raw_data, output_dir=output_dir)
    print(f"GTFS-RT generated at: {result_path}")
