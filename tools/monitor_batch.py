#!/usr/bin/env python3
"""Monitor OpenAI batch progress."""

import sys
import time
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def monitor_batch(batch_id):
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    print("Monitoring batch: {}".format(batch_id))
    print("Press Ctrl+C to stop monitoring\n")
    
    while True:
        try:
            batch = client.batches.retrieve(batch_id)
            
            # Clear screen and show status
            os.system('clear' if os.name == 'posix' else 'cls')
            
            created = datetime.fromtimestamp(batch.created_at).strftime('%Y-%m-%d %H:%M:%S')
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print("Batch Monitor - {}".format(now))
            print("=" * 50)
            print("Batch ID: {}".format(batch.id))
            print("Status: {}".format(batch.status))
            print("Created: {}".format(created))
            print("Total requests: {}".format(batch.request_counts.total))
            print("Completed: {}".format(batch.request_counts.completed))
            print("Failed: {}".format(batch.request_counts.failed))
            
            # Calculate progress
            if batch.request_counts.total > 0:
                progress = (batch.request_counts.completed / batch.request_counts.total) * 100
                print("Progress: {:.1f}%".format(progress))
            
            if batch.status == "completed":
                print("\n✅ Batch completed!")
                print("Output file ID: {}".format(batch.output_file_id))
                print("\nRun this to download results:")
                print("python3.8 submit_openai_batch.py {}".format(batch_id))
                break
            elif batch.status == "failed":
                print("\n❌ Batch failed!")
                if batch.errors:
                    print("Errors: {}".format(batch.errors))
                break
            elif batch.status == "expired":
                print("\n⏰ Batch expired!")
                break
            
            # Wait 30 seconds before next check
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            break
        except Exception as e:
            print("Error: {}".format(e))
            break

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3.8 monitor_batch.py <batch_id>")
        sys.exit(1)
    
    monitor_batch(sys.argv[1])