import os
import json
import pytest
from unittest.mock import patch, MagicMock
from src.validator import download_validator, run_validator

@patch("urllib.request.urlretrieve")
def test_download_validator(mock_urlretrieve, tmp_path):
    jar_path = str(tmp_path / "gtfs-validator.jar")
    download_validator(jar_path)
    mock_urlretrieve.assert_called_once()

@patch("src.validator.download_validator")
@patch("subprocess.run")
def test_run_validator_success(mock_run, mock_download, tmp_path):
    output_dir = tmp_path / "output"
    gtfs_zip = str(tmp_path / "gtfs.zip")
    
    # Mock the subprocess run to create a fake report.json
    def side_effect(*args, **kwargs):
        os.makedirs(output_dir, exist_ok=True)
        report_path = output_dir / "report.json"
        with open(report_path, "w") as f:
            json.dump({"notices": [{"severity": "INFO", "code": "some_info"}]}, f)
            
    mock_run.side_effect = side_effect
    
    report = run_validator(gtfs_zip, str(output_dir), jar_path="dummy.jar")
    
    assert mock_download.called
    assert mock_run.called
    assert len(report["notices"]) == 1

@patch("src.validator.download_validator")
@patch("subprocess.run")
def test_run_validator_errors(mock_run, mock_download, tmp_path):
    output_dir = tmp_path / "output_errors"
    gtfs_zip = str(tmp_path / "gtfs.zip")
    
    def side_effect(*args, **kwargs):
        os.makedirs(output_dir, exist_ok=True)
        report_path = output_dir / "report.json"
        with open(report_path, "w") as f:
            json.dump({"notices": [{"severity": "ERROR", "code": "missing_required_file"}]}, f)
            
    mock_run.side_effect = side_effect
    
    with pytest.raises(ValueError, match="GTFS Validation failed"):
        run_validator(gtfs_zip, str(output_dir), jar_path="dummy.jar")
