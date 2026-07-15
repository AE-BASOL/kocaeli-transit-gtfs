import json
import os
import re

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "operator_routes.json")

def load_overrides():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def classify_vehicle(bus: dict) -> dict:
    bus_out = dict(bus)
    route_code = bus_out.get("route_code")
    plate = bus_out.get("plate")
    
    overrides = load_overrides()
    
    operator = "Unknown"
    vehicle_type = "Unknown"
    
    if route_code and str(route_code) in overrides:
        override = overrides[str(route_code)]
        operator = override.get("operator", "Unknown")
        vehicle_type = override.get("vehicle_type", "Unknown")
    elif route_code and str(route_code).startswith("T"):
        operator = "Tram"
        vehicle_type = "Tram"
    elif plate and isinstance(plate, str):
        plate_upper = plate.upper()
        if "BR" in plate_upper or "BDB" in plate_upper:
            operator = "Municipality"
            vehicle_type = "Bus"
        elif re.search(r'(?:^|\s|\d)[JM](?:\s|\d|$)', plate_upper):
            operator = "Private"
            vehicle_type = "Bus"
            
    bus_out["operator"] = operator
    bus_out["vehicle_type"] = vehicle_type
    
    return bus_out
