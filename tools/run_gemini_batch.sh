#!/bin/bash

# Gemini Batch Prediction Script for SycoBench
# This script helps you run batch predictions with Gemini 2.5 Flash

echo "=== Gemini Batch Prediction Setup ==="
echo ""
echo "This will run 6,006 predictions (1,001 questions × 6 pressure levels each)"
echo "Estimated cost: ~\$0.07 for input + ~\$0.30 for output = ~\$0.37 total"
echo ""

# Check if user has set required variables
if [ -z "$PROJECT_ID" ]; then
    echo "Please set your Google Cloud project ID:"
    echo "export PROJECT_ID=your-project-id"
    exit 1
fi

if [ -z "$BUCKET_NAME" ]; then
    echo "Please set your Google Cloud Storage bucket name:"
    echo "export BUCKET_NAME=your-bucket-name"
    exit 1
fi

LOCATION=${LOCATION:-"us-central1"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
JOB_NAME="sycobench-gemini-batch-${TIMESTAMP}"
INPUT_FILE="gemini_batch_1000.jsonl"
GCS_INPUT="gs://${BUCKET_NAME}/sycobench/input/${INPUT_FILE}"
GCS_OUTPUT="gs://${BUCKET_NAME}/sycobench/output/${TIMESTAMP}/"

echo "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Bucket: $BUCKET_NAME"
echo "  Location: $LOCATION"
echo "  Job Name: $JOB_NAME"
echo ""

# Step 1: Upload JSONL to GCS
echo "Step 1: Uploading $INPUT_FILE to Google Cloud Storage..."
gsutil cp $INPUT_FILE $GCS_INPUT

if [ $? -ne 0 ]; then
    echo "Failed to upload file to GCS. Make sure:"
    echo "1. You have gsutil installed and configured"
    echo "2. You have write access to the bucket"
    exit 1
fi

echo "✓ File uploaded successfully"
echo ""

# Step 2: Create batch prediction job
echo "Step 2: Creating batch prediction job..."

cat > batch_request.json <<EOF
{
  "displayName": "${JOB_NAME}",
  "model": "publishers/google/models/gemini-1.5-flash-002",
  "inputConfig": {
    "instancesFormat": "jsonl",
    "gcsSource": {
      "uris": ["${GCS_INPUT}"]
    }
  },
  "outputConfig": {
    "predictionsFormat": "jsonl",
    "gcsDestination": {
      "outputUriPrefix": "${GCS_OUTPUT}"
    }
  }
}
EOF

echo "Request JSON created. Submitting batch job..."

# Submit the batch job
RESPONSE=$(curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @batch_request.json \
  "https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/batchPredictionJobs" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "Failed to create batch job. Make sure:"
    echo "1. You're authenticated with gcloud"
    echo "2. Vertex AI API is enabled"
    echo "3. You have necessary permissions"
    exit 1
fi

# Extract job ID from response
JOB_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['name'].split('/')[-1])" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
    echo "Failed to get job ID. Response:"
    echo "$RESPONSE"
    exit 1
fi

echo "✓ Batch job created successfully!"
echo "  Job ID: $JOB_ID"
echo ""

# Step 3: Monitor job
echo "Step 3: Monitoring job status..."
echo "You can check status with:"
echo "curl -X GET \\"
echo "  -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" \\"
echo "  https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/batchPredictionJobs/${JOB_ID}"
echo ""
echo "Or use this command to poll status:"
echo "watch -n 30 'curl -s -X GET -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/batchPredictionJobs/${JOB_ID} | python3 -m json.tool | grep -E \"(state|createTime|updateTime)\"'"
echo ""
echo "Output will be saved to: ${GCS_OUTPUT}"
echo ""
echo "Once complete, download results with:"
echo "gsutil -m cp -r ${GCS_OUTPUT} ./batch_results/"

# Save job info
cat > job_info.txt <<EOF
Job ID: $JOB_ID
Job Name: $JOB_NAME
Input: $GCS_INPUT
Output: $GCS_OUTPUT
Created: $(date)
Total Requests: 6,006
Estimated Cost: ~\$0.37
EOF

echo "Job information saved to job_info.txt"