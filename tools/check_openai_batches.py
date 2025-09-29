#!/usr/bin/env python3
"""Check all OpenAI batch jobs."""

import openai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    batches = client.batches.list()
    
    if not batches.data:
        print("No OpenAI batches found.")
    else:
        print("\nFound {} OpenAI batch(es):\n".format(len(batches.data)))
        print("-" * 80)
        
        for batch in batches.data:
            created = datetime.fromtimestamp(batch.created_at).strftime('%Y-%m-%d %H:%M:%S')
            print("Batch ID: {}".format(batch.id))
            print("Status: {}".format(batch.status))
            print("Created: {}".format(created))
            if batch.input_file_id:
                print("Input File ID: {}".format(batch.input_file_id))
            if batch.output_file_id:
                print("Output File ID: {}".format(batch.output_file_id))
            print("-" * 80)
            
except Exception as e:
    print("Error: {}".format(e))