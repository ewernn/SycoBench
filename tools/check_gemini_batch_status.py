#!/usr/bin/env python3
"""Check Gemini batch job status."""
import json
import subprocess
import sys
from datetime import datetime

def check_batch_status(job_id=None):
    """Check status of Gemini batch job."""
    
    # Load job info if no job_id provided
    if not job_id:
        try:
            with open("gemini_job_info.json", "r") as f:
                job_info = json.load(f)
                job_id = job_info["job_id"]
                project_id = job_info["project_id"]
                location = job_info["location"]
                output_path = job_info["output"]
        except FileNotFoundError:
            print("No gemini_job_info.json found. Please provide job ID.")
            return
    else:
        project_id = "pythea-460718"
        location = "us-central1"
        output_path = None
    
    # Get access token
    token_result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True
    )
    
    if token_result.returncode != 0:
        print("Failed to get token: {}".format(token_result.stderr))
        return
    
    access_token = token_result.stdout.strip()
    
    # Check job status
    url = "https://{}-aiplatform.googleapis.com/v1/projects/{}/locations/{}/batchPredictionJobs/{}".format(
        location, project_id, location, job_id
    )
    
    curl_cmd = [
        "curl", "-s", "-X", "GET",
        "-H", "Authorization: Bearer {}".format(access_token),
        url
    ]
    
    result = subprocess.run(curl_cmd, capture_output=True, text=True)
    
    try:
        job_data = json.loads(result.stdout)
        
        if "error" in job_data:
            print("Error: {}".format(job_data["error"]))
            return
        
        # Display status
        print("=== Gemini Batch Job Status ===")
        print("Job ID: {}".format(job_id))
        print("Name: {}".format(job_data.get("displayName", "N/A")))
        print("State: {}".format(job_data.get("state", "UNKNOWN")))
        
        if "createTime" in job_data:
            create_time = datetime.fromisoformat(job_data["createTime"].rstrip("Z"))
            print("Created: {}".format(create_time.strftime("%Y-%m-%d %H:%M:%S")))
        
        if "startTime" in job_data:
            start_time = datetime.fromisoformat(job_data["startTime"].rstrip("Z"))
            print("Started: {}".format(start_time.strftime("%Y-%m-%d %H:%M:%S")))
        
        if "endTime" in job_data:
            end_time = datetime.fromisoformat(job_data["endTime"].rstrip("Z"))
            print("Ended: {}".format(end_time.strftime("%Y-%m-%d %H:%M:%S")))
        
        if "error" in job_data:
            print("\n❌ Job failed with error:")
            print("Code: {}".format(job_data["error"].get("code", "Unknown")))
            print("Message: {}".format(job_data["error"].get("message", "Unknown")))
        
        if job_data.get("state") == "JOB_STATE_SUCCEEDED":
            print("\n✅ Job completed successfully!")
            if output_path:
                print("\nDownload results with:")
                print("gsutil -m cp -r {} ./batch_results/".format(output_path))
        elif job_data.get("state") == "JOB_STATE_RUNNING":
            print("\n⏳ Job is running...")
        elif job_data.get("state") == "JOB_STATE_PENDING":
            print("\n⏳ Job is pending...")
            
    except json.JSONDecodeError:
        print("Failed to parse response")
        print(result.stdout)

if __name__ == "__main__":
    job_id = sys.argv[1] if len(sys.argv) > 1 else None
    check_batch_status(job_id)