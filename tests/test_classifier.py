import pytest
from src.crawler.classifier import classify_vehicle

def test_classify_tram():
    bus = {"route_code": "T1", "plate": "41 TRAM 01"}
    result = classify_vehicle(bus)
    assert result["operator"] == "Tram"
    assert result["vehicle_type"] == "Tram"

def test_classify_private_bus_j():
    bus = {"route_code": "100", "plate": "41 J 1234"}
    result = classify_vehicle(bus)
    assert result["operator"] == "Private"
    assert result["vehicle_type"] == "Bus"

def test_classify_private_bus_m():
    bus = {"route_code": "100", "plate": "41M456"}
    result = classify_vehicle(bus)
    assert result["operator"] == "Private"
    assert result["vehicle_type"] == "Bus"

def test_classify_municipality_bus_br():
    bus = {"route_code": "200", "plate": "41 BR 567"}
    result = classify_vehicle(bus)
    assert result["operator"] == "Municipality"
    assert result["vehicle_type"] == "Bus"

def test_classify_municipality_bus_bdb():
    bus = {"route_code": "200", "plate": "41BDB890"}
    result = classify_vehicle(bus)
    assert result["operator"] == "Municipality"
    assert result["vehicle_type"] == "Bus"

def test_classify_unknown():
    bus = {"route_code": "300", "plate": "34 ABC 12"}
    result = classify_vehicle(bus)
    assert result["operator"] == "Unknown"
    assert result["vehicle_type"] == "Unknown"

def test_classify_missing_fields():
    bus = {}
    result = classify_vehicle(bus)
    assert result["operator"] == "Unknown"
    assert result["vehicle_type"] == "Unknown"

    bus = {"route_code": None, "plate": None}
    result = classify_vehicle(bus)
    assert result["operator"] == "Unknown"
    assert result["vehicle_type"] == "Unknown"
