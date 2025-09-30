# Comprehensive Batch Processing Guide for SycoBench

*Last Updated: July 2025*

This guide provides step-by-step instructions for running batch processing jobs across all supported providers. Batch processing allows you to test thousands of questions at significant cost savings.

## Table of Contents
1. [Overview](#overview)
2. [OpenAI Batch Processing](#openai-batch-processing)
3. [Anthropic Batch Processing](#anthropic-batch-processing)
4. [Google Gemini Batch Processing](#google-gemini-batch-processing)
5. [Batch Status Management](#batch-status-management)
6. [Cost Optimization Strategies](#cost-optimization-strategies)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### Benefits of Batch Processing
- **Cost Savings**: 50-96% reduction in API costs
- **Scale**: Test 1000+ questions in a single job
- **Reliability**: Automatic retries for failed requests
- **Efficiency**: Process large datasets without rate limits

### Quick Comparison

| Provider | Discount | Setup Complexity | Turnaround |
|----------|----------|------------------|------------|
| OpenAI | 50% | Easy | 24 hours |
| Anthropic | 0% (coming) | Easy | 24 hours |
| Google | 50-96% | Complex | 24 hours |
| xAI | N/A | N/A | N/A |

---

## OpenAI Batch Processing

### Prerequisites
- OpenAI API key with billing enabled
- Python 3.8+
- SycoBench installed

### Step 1: Create Batch File
```bash
# For a specific model
python src/batch/batch_creator.py \
    --provider openai \
    --model gpt-4.1-mini \
    --questions data/datasets/safety_questions_1000.txt \
    --output openai_batch.jsonl

# For multiple models (create separate files)
for model in gpt-5 gpt-5-mini gpt-5-nano; do
    python src/batch/batch_creator.py \
        --provider openai \
        --model $model \
        --questions data/datasets/safety_questions_1000.txt \
        --output openai_batch_${model}.jsonl
done
```

### Step 2: Submit Batch Job
```bash
# Using batch manager
python src/batch/batch_manager.py \
    --provider openai \
    --action create \
    --input openai_batch.jsonl \
    --description "Safety test GPT-4.1-mini"

# Save the batch ID that's returned!
```

### Step 3: Monitor Progress
```bash
# Check status once
python src/batch/batch_manager.py \
    --provider openai \
    --action check \
    --batch-id batch_abc123

# Monitor until completion
python src/batch/batch_manager.py \
    --provider openai \
    --action monitor \
    --batch-id batch_abc123 \
    --interval 300  # Check every 5 minutes
```

### Step 4: Download Results
```bash
# Results are auto-downloaded when monitoring completes
# Or manually download:
python src/batch/batch_manager.py \
    --provider openai \
    --action download \
    --batch-id batch_abc123 \
    --output results/openai_batch_results.jsonl
```

### Step 5: Process Results
```bash
python src/batch/batch_processor.py \
    --input results/openai_batch_results.jsonl \
    --output results/openai_analysis.json
```

### OpenAI Batch Format
```json
{
    "custom_id": "question_1_pressure_0",
    "method": "POST",
    "url": "/v1/chat/completions",
    "body": {
        "model": "gpt-4.1-mini",
        "messages": [...],
        "temperature": 0.0
    }
}
```

---

## Anthropic Batch Processing

### Prerequisites
- Anthropic API key
- Batch API access (check availability)

### Step 1: Create Batch File
```bash
python src/batch/batch_creator.py \
    --provider claude \
    --model claude-sonnet-4 \
    --questions data/datasets/safety_questions_1000.txt \
    --output claude_batch.jsonl
```

### Step 2: Submit Batch
```bash
python src/batch/batch_manager.py \
    --provider claude \
    --action create \
    --input claude_batch.jsonl \
    --description "Safety test Claude Sonnet 4"
```

### Step 3: Monitor and Download
```bash
# Monitor
python src/batch/batch_manager.py \
    --provider claude \
    --action monitor \
    --batch-id msgbatch_abc123

# Results download automatically when complete
```

### Anthropic Batch Format
```json
{
    "custom_id": "question_1_pressure_0",
    "params": {
        "model": "claude-sonnet-4-20241229",
        "messages": [...],
        "temperature": 0.0,
        "max_tokens": 1000
    }
}
```

---

## Google Gemini Batch Processing

### Prerequisites
- Google Cloud Project with billing enabled
- Vertex AI API enabled
- Cloud Storage bucket created
- `gcloud` CLI installed and configured

### Step 1: Set Up Environment
```bash
# Set environment variables
export PROJECT_ID="your-gcp-project"
export BUCKET_NAME="your-gcs-bucket"
export REGION="us-central1"

# Verify setup
gcloud config set project $PROJECT_ID
gcloud auth application-default login
```

### Step 2: Create Batch File
```bash
# Create Gemini-specific batch format
python src/batch/batch_creator.py \
    --provider gemini \
    --model gemini-2.5-flash \
    --questions data/datasets/safety_questions_1000.txt \
    --output gemini_batch.jsonl
```

### Step 3: Upload to Cloud Storage
```bash
# Upload input file
gsutil cp gemini_batch.jsonl gs://$BUCKET_NAME/input/

# Create output directory
gsutil mkdir -p gs://$BUCKET_NAME/output/
```

### Step 4: Submit Batch Job
```bash
# Using the provided script
./scripts/run_gemini_batch.sh

# Or manually with gcloud
gcloud ai models batch-predict \
    --model=gemini-2-5-flash \
    --input-format=jsonl \
    --gcs-source=gs://$BUCKET_NAME/input/gemini_batch.jsonl \
    --gcs-destination=gs://$BUCKET_NAME/output/ \
    --region=$REGION
```

### Step 5: Monitor Job
```bash
# List batch jobs
gcloud ai models batch-predict-jobs list --region=$REGION

# Check specific job
gcloud ai models batch-predict-jobs describe JOB_ID --region=$REGION
```

### Step 6: Download Results
```bash
# Download when complete
gsutil cp -r gs://$BUCKET_NAME/output/ ./results/gemini/

# Process results
python src/batch/batch_processor.py \
    --input results/gemini/predictions.jsonl \
    --output results/gemini_analysis.json \
    --provider gemini
```

### Gemini Batch Format
```json
{
    "request": {
        "contents": [{
            "parts": [{
                "text": "Is it safe to..."
            }]
        }],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 1000
        }
    }
}
```

---

## Batch Status Management

### Check All Batch Jobs
```bash
# See status of all batch jobs
python scripts/batch_benchmark.py status
```

### Track Multiple Batches
Create a tracking file `batch_tracking.json`:
```json
{
    "batches": [
        {
            "provider": "openai",
            "batch_id": "batch_abc123",
            "model": "gpt-4.1-mini",
            "created": "2025-07-18T10:00:00Z",
            "status": "in_progress"
        },
        {
            "provider": "claude",
            "batch_id": "msgbatch_xyz789",
            "model": "claude-sonnet-4",
            "created": "2025-07-18T11:00:00Z",
            "status": "pending"
        }
    ]
}
```

### Automated Status Checking Script
```bash
#!/bin/bash
# check_all_batches.sh

# Check OpenAI batches
for batch_id in $(cat batch_tracking.json | jq -r '.batches[] | select(.provider=="openai") | .batch_id'); do
    echo "Checking OpenAI batch: $batch_id"
    python src/batch/batch_manager.py --provider openai --action check --batch-id $batch_id
done

# Check Claude batches
for batch_id in $(cat batch_tracking.json | jq -r '.batches[] | select(.provider=="claude") | .batch_id'); do
    echo "Checking Claude batch: $batch_id"
    python src/batch/batch_manager.py --provider claude --action check --batch-id $batch_id
done
```

---

## Cost Optimization Strategies

### 1. Model Selection Strategy
```bash
# Test progression: Start cheap, escalate if needed

# Phase 1: Ultra-low cost screening ($0.87 total)
- Gemini 2.5 Flash (batch): $0.37
- GPT-4.1-nano (batch): $0.50

# Phase 2: If concerning results found ($3.25 total)
- GPT-4.1-mini (batch): $2.00
- Claude Haiku 3.5: $1.25

# Phase 3: Deep analysis of problematic models ($15+ each)
- Claude Sonnet 4: $9.00
- GPT-4o-mini: $0.75 (batch)
```

### 2. Question Batching Strategy
```python
# Split questions by priority
high_priority_questions = safety_questions[:100]  # Most critical
medium_priority = safety_questions[100:500]       # Important
low_priority = safety_questions[500:]            # Comprehensive

# Test high-priority first across all models
# Only proceed with full set for concerning models
```

### 3. Optimal Batch Sizes

| Provider | Optimal Size | Max Size | Notes |
|----------|-------------|----------|-------|
| OpenAI | 1000-5000 | 50,000 | Larger batches = better reliability |
| Anthropic | 1000-2000 | 10,000 | New API, start smaller |
| Google | 1000 | Unlimited | Costs same regardless of size |

---

## Troubleshooting

### Common Issues and Solutions

#### OpenAI Batch Failures
```bash
# Check error file if batch partially fails
python src/batch/batch_manager.py \
    --provider openai \
    --action check \
    --batch-id batch_abc123

# Download error details
if [ ! -z "$ERROR_FILE_ID" ]; then
    python -c "
import openai
client = openai.OpenAI()
errors = client.files.content('$ERROR_FILE_ID')
print(errors.content.decode())
" > batch_errors.jsonl
fi
```

#### Anthropic Rate Limits
```python
# Add retry logic for batch creation
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=60))
def create_claude_batch(requests):
    return client.messages.batches.create(requests=requests)
```

#### Google Cloud Permissions
```bash
# Fix common permission issues
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:your-email@example.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:your-email@example.com" \
    --role="roles/storage.objectAdmin"
```

### Monitoring Best Practices

1. **Set up alerts**:
```bash
# Email notification when batch completes
while true; do
    STATUS=$(python src/batch/batch_manager.py --provider openai --action check --batch-id $BATCH_ID | grep status | awk '{print $2}')
    if [ "$STATUS" = "completed" ]; then
        echo "Batch $BATCH_ID completed" | mail -s "Batch Complete" your-email@example.com
        break
    fi
    sleep 300
done &
```

2. **Log all batch jobs**:
```bash
# Append to batch log
echo "$(date),openai,$BATCH_ID,$MODEL,created" >> batch_log.csv
```

3. **Track costs**:
```python
# Calculate batch costs
def calculate_batch_cost(provider, model, num_requests):
    costs = {
        "openai": {
            "gpt-5-nano": 0.21 / 1000,    # per request with 50% discount
            "gpt-5-mini": 1.05 / 1000,
            "gpt-5": 3.00 / 1000
        },
        "gemini": {
            "gemini-2.5-flash": 0.37 / 1000,
            "gemini-2.5-pro": 12.50 / 1000
        }
    }
    return costs.get(provider, {}).get(model, 0) * num_requests
```

---

## Quick Reference

### Start a Full Benchmark
```bash
# 1. Create batch configuration
python scripts/batch_benchmark.py

# 2. Submit all batches
./scripts/submit_all_batches.sh

# 3. Monitor progress
python scripts/batch_benchmark.py status

# 4. Process all results when complete
python scripts/process_all_results.py
```

### Emergency Commands
```bash
# Cancel OpenAI batch
curl -X POST https://api.openai.com/v1/batches/$BATCH_ID/cancel \
    -H "Authorization: Bearer $OPENAI_API_KEY"

# Download partial results
python src/batch/batch_manager.py \
    --provider openai \
    --action download \
    --batch-id $BATCH_ID \
    --output partial_results.jsonl \
    --force
```

Remember: Always test with a small batch (10-20 questions) first before running full 1000-question batches!