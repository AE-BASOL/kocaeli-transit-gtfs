import os
import subprocess
import urllib.request
import json
from typing import Dict, Any

VALIDATOR_URL = "https://github.com/MobilityData/gtfs-validator/releases/download/v6.0.0/gtfs-validator-6.0.0-cli.jar"
VALIDATOR_JAR = "gtfs-validator.jar"

def download_validator(jar_path: str = VALIDATOR_JAR):
    if not os.path.exists(jar_path):
        print(f"Downloading GTFS validator to {jar_path}...")
        urllib.request.urlretrieve(VALIDATOR_URL, jar_path)

def run_validator(gtfs_zip: str, output_dir: str, jar_path: str = VALIDATOR_JAR) -> Dict[str, Any]:
    download_validator(jar_path)
    
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        "java", "-jar", jar_path,
        "-i", gtfs_zip,
        "-o", output_dir
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        # The validator might return non-zero exit code if there are errors, which is expected.
        pass
        
    report_path = os.path.join(output_dir, "report.json")
    if not os.path.exists(report_path):
        raise FileNotFoundError("Validator report.json not found. Did the validator run successfully?")
        
    with open(report_path, "r") as f:
        report = json.load(f)
        
    # Check for critical errors
    errors = []
    if "notices" in report:
        for notice in report["notices"]:
            if notice.get("severity") == "ERROR":
                errors.append(notice)
                
    if errors:
        raise ValueError(f"GTFS Validation failed with {len(errors)} critical errors: {errors}")
        
    return report

if __name__ == "__main__":
    gtfs_zip = "output/gtfs.zip"
    output_dir = "output/validator_report"
    
    if os.path.exists(gtfs_zip):
        print(f"Running validator on {gtfs_zip}...")
        try:
            report = run_validator(gtfs_zip, output_dir=output_dir)
            print("Validation completed successfully.")
        except Exception as e:
            print(f"Validation failed: {e}")
            exit(1)
    else:
        print(f"Error: {gtfs_zip} not found. Ensure static GTFS generation ran successfully.")
        exit(1)
