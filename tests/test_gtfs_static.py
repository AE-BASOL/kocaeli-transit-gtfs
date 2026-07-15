import os
import zipfile
from src.static_gtfs import generate_static_gtfs

def test_generate_static_gtfs(tmp_path):
    output_dir = tmp_path / "data"
    raw_data = [{"route_code": "1", "label": "İzmit - Umuttepe"}]
    
    zip_path = generate_static_gtfs(raw_data, output_dir=str(output_dir))
    
    assert os.path.exists(zip_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        namelist = zf.namelist()
        assert "agency.txt" in namelist
        assert "stops.txt" in namelist
        assert "routes.txt" in namelist
        assert "trips.txt" in namelist
        assert "stop_times.txt" in namelist
        assert "calendar.txt" in namelist
