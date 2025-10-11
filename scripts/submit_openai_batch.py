#!/usr/bin/env python3
"""
Submit OpenAI batch job and monitor progress
"""
import os
import time
from openai import OpenAI
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def submit_batch(jsonl_file='openai_batch_1000.jsonl'):
    """Submit batch job to OpenAI"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please check your .env file")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    # Upload the file
    print(f"Uploading {jsonl_file}...")
    with open(jsonl_file, 'rb') as f:
        file_response = client.files.create(
            file=f,
            purpose='batch'
        )
    
    print(f"File uploaded: {file_response.id}")
    
    # Create batch job
    print("Creating batch job...")
    batch_response = client.batches.create(
        input_file_id=file_response.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    
    print(f"\nBatch job created!")
    print(f"Batch ID: {batch_response.id}")
    print(f"Status: {batch_response.status}")
    
    return batch_response.id

def check_batch_status(batch_id):
    """Check status of batch job"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    batch = client.batches.retrieve(batch_id)
    
    print(f"\nBatch Status: {batch.status}")
    print(f"Created: {batch.created_at}")
    
    if batch.request_counts:
        print(f"Total requests: {batch.request_counts.total}")
        print(f"Completed: {batch.request_counts.completed}")
        print(f"Failed: {batch.request_counts.failed}")
    
    if batch.status == 'completed':
        print(f"\n✅ Batch completed!")
        print(f"Output file ID: {batch.output_file_id}")
        if batch.error_file_id:
            print(f"Error file ID: {batch.error_file_id}")
            
        # Download results
        if batch.output_file_id:
            print("\nDownloading results...")
            output = client.files.content(batch.output_file_id)
            
            output_filename = f"batch_results_{batch_id}.jsonl"
            with open(output_filename, 'wb') as f:
                f.write(output.content)
            
            print(f"Results saved to: {output_filename}")
            return output_filename
    
    elif batch.status == 'failed':
        print(f"\n❌ Batch failed!")
        if batch.errors:
            print(f"Error: {batch.errors}")
    
    return None

def monitor_batch(batch_id, check_interval=60):
    """Monitor batch until completion"""
    print(f"\nMonitoring batch {batch_id}...")
    print("This may take several hours. You can safely exit and check later.")
    
    while True:
        result_file = check_batch_status(batch_id)
        if result_file:
            return result_file
        
        print(f"\nWaiting {check_interval} seconds before next check...")
        time.sleep(check_interval)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.endswith('.jsonl'):
            # Submit new batch with custom file
            batch_id = submit_batch(arg)
            print("\nTo check status later, run:")
            print(f"python3.8 submit_openai_batch.py {batch_id}")
        else:
            # Check existing batch
            batch_id = arg
            check_batch_status(batch_id)
    else:
        # Submit new batch with default file
        batch_id = submit_batch()
        
        print("\nTo check status later, run:")
        print(f"python3.8 submit_openai_batch.py {batch_id}")
        
        # Optional: monitor until completion
        # monitor_batch(batch_id)