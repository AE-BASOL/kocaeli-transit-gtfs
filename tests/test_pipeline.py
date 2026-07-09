import os
import yaml
import pytest

def test_workflow_file_exists():
    assert os.path.exists(".github/workflows/gtfs-pipeline.yml")

def test_workflow_is_valid_yaml():
    with open(".github/workflows/gtfs-pipeline.yml", "r") as f:
        workflow = yaml.safe_load(f)
    assert isinstance(workflow, dict)
    assert "jobs" in workflow
