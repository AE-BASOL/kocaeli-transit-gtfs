import os
from google.transit import gtfs_realtime_pb2
from src.rt_gtfs import generate_rt_gtfs

def test_generate_rt_gtfs(tmp_path):
    output_dir = tmp_path / "data"
    live_data = [
        {
            "route_code": "1",
            "lat": 40.7654,
            "lon": 29.9408,
            "plate": "41 TEST 001",
        }
    ]
    
    pb_path = generate_rt_gtfs(live_data, output_dir=str(output_dir))
    
    assert os.path.exists(pb_path)
    
    feed = gtfs_realtime_pb2.FeedMessage()
    with open(pb_path, "rb") as f:
        feed.ParseFromString(f.read())
        
    assert feed.header.gtfs_realtime_version == "2.0"
    assert len(feed.entity) > 0
    
    entity = feed.entity[0]
    assert entity.trip_update.trip.trip_id == "trip_1"
    assert entity.vehicle.trip.trip_id == "trip_1"
    assert round(entity.vehicle.position.latitude, 4) == 40.7654
