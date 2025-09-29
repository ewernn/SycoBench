#!/usr/bin/env python3
"""Submit fixed Gemini batch to Vertex AI."""
import os
import json
import subprocess
from datetime import datetime

def submit_gemini_batch():
    """Submit Gemini batch job to Vertex AI."""
    
    # Configuration
    PROJECT_ID = "pythea-460718"  # From gcloud config
    BUCKET_NAME = "pythea-sycobench-1749689243"
    LOCATION = "us-central1"
    TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
    JOB_NAME = "sycobench-gemini-fixed-{}".format(TIMESTAMP)
    INPUT_FILE = "gemini_batch_fixed.jsonl"
    GCS_INPUT = "gs://{}/sycobench/input/{}".format(BUCKET_NAME, INPUT_FILE)
    GCS_OUTPUT = "gs://{}/sycobench/output/{}/".format(BUCKET_NAME, TIMESTAMP)
    
    print("=== Gemini Batch Submission (Fixed Format) ===")
    print("Project ID: {}".format(PROJECT_ID))
    print("Bucket: {}".format(BUCKET_NAME))
    print("Job Name: {}".format(JOB_NAME))
    print("Input: {}".format(GCS_INPUT))
    print("Output: {}".format(GCS_OUTPUT))
    print("")
    
    # Step 1: Upload to GCS
    print("Step 1: Uploading to GCS...")
    result = subprocess.run(
        ["gsutil", "cp", INPUT_FILE, GCS_INPUT],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Failed to upload: {}".format(result.stderr))
        return False
    
    print("✓ File uploaded successfully")
    print("")
    
    # Step 2: Create batch request
    batch_request = {
        "displayName": JOB_NAME,
        "model": "publishers/google/models/gemini-1.5-flash-002",
        "inputConfig": {
            "instancesFormat": "jsonl",
            "gcsSource": {
                "uris": [GCS_INPUT]
            }
        },
        "outputConfig": {
            "predictionsFormat": "jsonl",
            "gcsDestination": {
                "outputUriPrefix": GCS_OUTPUT
            }
        }
    }
    
    # Save request for debugging
    with open("batch_request_fixed.json", "w") as f:
        json.dump(batch_request, f, indent=2)
    
    # Step 3: Get access token
    print("Step 2: Getting access token...")
    token_result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True
    )
    
    if token_result.returncode != 0:
        print("Failed to get token: {}".format(token_result.stderr))
        return False
    
    access_token = token_result.stdout.strip()
    
    # Step 4: Submit batch job
    print("Step 3: Submitting batch job...")
    url = "https://{}-aiplatform.googleapis.com/v1/projects/{}/locations/{}/batchPredictionJobs".format(
        LOCATION, PROJECT_ID, LOCATION
    )
    
    curl_cmd = [
        "curl", "-X", "POST",
        "-H", "Authorization: Bearer {}".format(access_token),
        "-H", "Content-Type: application/json; charset=utf-8",
        "-d", "@batch_request_fixed.json",
        url
    ]
    
    result = subprocess.run(curl_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Failed to submit: {}".format(result.stderr))
        return False
    
    try:
        response = json.loads(result.stdout)
        if "error" in response:
            print("Error from API: {}".format(response["error"]))
            return False
        
        job_id = response["name"].split("/")[-1]
        
        print("✓ Batch job created successfully!")
        print("Job ID: {}".format(job_id))
        print("")
        
        # Save job info
        job_info = {
            "job_id": job_id,
            "job_name": JOB_NAME,
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "input": GCS_INPUT,
            "output": GCS_OUTPUT,
            "created": datetime.now().isoformat(),
            "total_requests": 6006,
            "estimated_cost": 0.26
        }
        
        with open("gemini_job_info.json", "w") as f:
            json.dump(job_info, f, indent=2)
        
        print("Job info saved to gemini_job_info.json")
        print("")
        print("To check status:")
        print("python3.8 check_gemini_batch_status.py")
        print("")
        print("Once complete, download with:")
        print("gsutil -m cp -r {} ./batch_results/".format(GCS_OUTPUT))
        
        return True
        
    except json.JSONDecodeError:
        print("Failed to parse response: {}".format(result.stdout))
        return False

if __name__ == "__main__":
    submit_gemini_batch()