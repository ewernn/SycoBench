# Provider-Specific API Details

This document preserves important API testing information, configuration details, and troubleshooting guidance for each provider supported by SycoBench.

## OpenAI API

### Configuration
- **Authentication**: Uses `OPENAI_API_KEY` environment variable
- **Models**: gpt-4.1-nano, gpt-4.1-mini, gpt-4o-mini, gpt-3.5-turbo, gpt-4.1
- **Temperature**: 0.0 for consistent results
- **System Messages**: Includes system role: "You are a helpful assistant."

### Batch Processing
- **Format**: JSONL with `custom_id`, `method`, `url`, and `body` fields
- **Endpoint**: `/v1/chat/completions`
- **Token Limits**: 200,000 tokens per batch maximum
- **Processing Time**: Up to 24 hours for completion
- **Cost Advantage**: 50% discount on batch processing
- **Reasoning Control**: Supports `"reasoning": False` parameter

### Testing Procedures
```python
# Simple API test
client = openai.OpenAI(api_key=api_key)
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello! This is a test message."}],
    max_tokens=50,
    temperature=0
)
```

### Troubleshooting
1. **Rate Limits**: Check platform.openai.com/account/limits
2. **Usage Limits**: Ensure monthly usage limit > $0
3. **API Key Issues**: Try creating new API key
4. **Organization**: Check organization membership
5. **Credits**: Verify credit allocation

### Cost Calculation
- **Token-based pricing**: Per-token rates vary by model
- **Batch discount**: 50% discount applied automatically
- **Estimation**: ~100 input tokens, ~150-200 output tokens per request

## Claude API (Anthropic)

### Configuration
- **Authentication**: Uses `ANTHROPIC_API_KEY` environment variable
- **Models**: claude-opus-4, claude-sonnet-4, claude-haiku-3.5
- **Temperature**: 0.0 for consistency
- **Max Tokens**: 500 tokens for responses
- **No System Messages**: Direct user/assistant conversation format

### Model Name Mapping
```python
model_mapping = {
    "opus-4": "claude-opus-4-20250514",
    "sonnet-4": "claude-sonnet-4-20250514", 
    "haiku-3.5": "claude-haiku-3.5-20240829"
}
```

### Batch Processing
- **Format**: JSONL with `custom_id` and `params` fields
- **Processing**: Uses `client.messages.batches.create()` method
- **Status Tracking**: Includes `processing_status` field
- **Cost Advantage**: 50% discount on batch processing

### Testing Procedures
```python
# Simple API test
client = anthropic.Anthropic(api_key=api_key)
response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=50,
    temperature=0,
    messages=[{"role": "user", "content": "Hello! This is a test message."}]
)
```

### Troubleshooting
- **Beta API Access**: Message Batches may require specific API access
- **Alternative Approaches**: Try fallback methods when primary API fails
- **AnthropicBedrock**: Alternative client for specific use cases

### Cost Calculation
- **Token-based pricing**: Input/output rates vary by model
- **Batch discount**: 50% discount applied
- **Estimation**: ~500 tokens per response

## Gemini API (Google)

### Configuration
- **Authentication**: Uses `GOOGLE_API_KEY` environment variable
- **Models**: gemini-1.5-flash, gemini-2.5-flash, gemini-2.5-pro
- **Content Structure**: Nested `contents` with `role` and `parts` arrays
- **Text Wrapping**: Text content wrapped in `{"text": "content"}` format

### Batch Processing
- **Format**: JSONL with only `request` field (Vertex AI requirement)
- **Content Structure**: 
  ```python
  {
    "request": {
      "contents": [
        {
          "role": "user",
          "parts": [{"text": "question"}]
        }
      ]
    }
  }
  ```
- **Storage Requirements**: Files must be uploaded to Google Cloud Storage
- **Processing**: Uses external shell scripts for job submission

### Testing Procedures
```python
# Simple API test
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Hello! This is a test message.")
```

### Troubleshooting
- **Format Requirements**: Strict adherence to Vertex AI format
- **Google Cloud Storage**: Requires file upload to GCS before batch processing
- **Shell Script Integration**: Uses external scripts for batch submission

### Cost Calculation
- **Character-based pricing**: $0.0125 per million input characters, $0.05 per million output characters
- **No Batch Discount**: Full pricing applies
- **Estimation**: ~500 input characters, ~750 output characters per request

## Grok API (xAI)

### Configuration
- **Authentication**: Uses `XAI_API_KEY` environment variable
- **Models**: grok-beta, grok-2, grok-3-mini
- **API**: OpenAI-compatible API
- **Base URL**: https://api.x.ai/v1

### Testing Procedures
```python
# Simple API test
client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1"
)
response = client.chat.completions.create(
    model="grok-beta",
    messages=[{"role": "user", "content": "Hello! This is a test message."}],
    max_tokens=50,
    temperature=0
)
```

### Limitations
- **Batch API**: Not available for Grok
- **Processing**: Only supports real-time API calls

## Special Requirements and Edge Cases

### Token/Character Limits
- **OpenAI**: 200,000 token limit per batch, requires subset creation for large datasets
- **Claude**: No explicit limits mentioned, but uses smaller test batches
- **Gemini**: No token limits, uses character-based estimation

### Batch Size Management
- **OpenAI Subset Strategy**: Split into 100-question batches for token conservation
- **Reduced Pressure Testing**: Uses only 3 pressure phrases instead of 5 for large batches
- **Small Test Batches**: All providers support small test versions (3-5 questions)

### Conversation History Handling
- **OpenAI**: Includes full conversation history with placeholder responses
- **Claude**: Similar conversation building with assistant response placeholders
- **Gemini**: Builds conversation arrays with user/model role structure

## Testing Commands

### Unified API Test
```bash
# Test all providers
python tests/test_api_connectivity.py --provider all --verbose

# Test specific provider
python tests/test_api_connectivity.py --provider openai --verbose
```

### Batch Processing Test
```bash
# Create batch file
python src/sycobench/batch/batch_creator.py --provider openai --model gpt-4o-mini --size small

# Manage batch job
python src/sycobench/batch/batch_manager.py --provider openai --action create --input batch.jsonl
```

## Migration Notes

This document consolidates information from:
- `test_openai_simple.py` → OpenAI testing procedures
- `test_claude_batch_api.py` → Claude batch API details
- `create_*_batch_*.py` files → Provider-specific batch formats
- Various batch processing scripts → Batch management procedures

All functionality has been preserved in the new unified scripts while maintaining provider-specific configurations and requirements.