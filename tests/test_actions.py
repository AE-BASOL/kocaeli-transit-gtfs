import os
import yaml
import pytest

def test_workflow_has_build_job():
    with open(".github/workflows/gtfs-pipeline.yml", "r") as f:
        workflow = yaml.safe_load(f)
    assert "build-and-validate" in workflow["jobs"]

def test_cron_schedule():
    with open(".github/workflows/gtfs-pipeline.yml", "r") as f:
        workflow = yaml.safe_load(f)
    assert "schedule" in workflow.get("on", {})
