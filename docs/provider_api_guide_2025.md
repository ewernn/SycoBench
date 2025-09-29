# Model Provider API Guide 2025

*Last Updated: July 2025*

This guide provides comprehensive information about each AI model provider's API capabilities, batch processing features, and the latest available models.

## Table of Contents
1. [Anthropic (Claude)](#anthropic-claude)
2. [OpenAI](#openai)
3. [Google (Gemini)](#google-gemini)
4. [xAI (Grok)](#xai-grok)
5. [Batch Processing Comparison](#batch-processing-comparison)
6. [Cost Analysis](#cost-analysis)
7. [API Limits & Rate Limiting](#api-limits--rate-limiting)

---

## Anthropic (Claude)

### Latest Models (July 2025)
- **Claude Opus 4** (`claude-opus-4-20250514`) - Most powerful, best safety alignment
- **Claude Sonnet 4** (`claude-sonnet-4-20241229`) - Balanced performance, 64K output
- **Claude Haiku 3.5** (`claude-3-5-haiku-20241022`) - Fast and cost-effective
- **Claude Sonnet 3.5** (`claude-3-5-sonnet-20241022`) - Previous generation

### API Features
- **Message Batches API**: Yes (50% cost savings)
- **Streaming**: Yes
- **Function Calling**: Yes
- **Vision**: Yes
- **Max Context**: 200K tokens
- **Output Limit**: 64K tokens (Sonnet 4), 32K tokens (Opus 4), 4K tokens (others)
- **Tokenizer**: Claude tokenizer (~3.5 characters per token)

### Batch Processing
```python
# Create batch
client.messages.batches.create(requests=[...])

# Check status
batch = client.messages.batches.retrieve(batch_id)

# Get results
results = client.messages.batches.results(batch_id)
```

### Pricing (per 1M tokens)
- **Claude Opus 4**: $15 input / $75 output
- **Claude Sonnet 4**: $3 input / $15 output
- **Claude Haiku 3.5**: $0.25 input / $1.25 output

### Token Counting
```python
import anthropic

client = anthropic.Anthropic(api_key="YOUR_KEY")

# Anthropic's token counting
token_count = client.count_tokens("Your text here")
print(f"Token count: {token_count}")

# Note: Anthropic uses their own tokenizer
# 1 token ≈ 3.5 characters for English text
```

---

## OpenAI

### Latest Models (July 2025)
- **GPT-4.1** - Latest flagship with 1M context window
- **GPT-4.1-nano** - Ultra-efficient mini model
- **GPT-4.1-mini** - Enhanced mini with better reasoning
- **GPT-4o** - Multimodal with efficient tokenizer
- **GPT-4o-mini** - Optimized multimodal mini
- **o3** - Reasoning model with thinking tokens
- **o4-mini** - Efficient reasoning model
- **GPT-3.5-turbo** - Legacy but still supported

### API Features
- **Batch API**: Yes (50% discount)
- **Streaming**: Yes
- **Function Calling**: Yes
- **Vision**: Yes (4o models)
- **Max Context**: 1M tokens (GPT-4.1), 128K tokens (others)
- **Output Limit**: 16K tokens (most models), 65K tokens (o-series)
- **Tokenizers**: cl100k_base (GPT-4.1), o200k_base (GPT-4o)

### Batch Processing
```python
# Upload file
file = client.files.create(file=open("batch.jsonl", "rb"), purpose="batch")

# Create batch
batch = client.batches.create(
    input_file_id=file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"
)

# Check status
status = client.batches.retrieve(batch.id)

# Download results
if status.status == "completed":
    results = client.files.content(status.output_file_id)
```

### Pricing (per 1M tokens)
- **GPT-4.1**: $5 input / $15 output (batch: 50% off)
- **GPT-4.1-nano**: $0.15 input / $0.45 output (batch: 50% off)
- **GPT-4.1-mini**: $0.60 input / $1.80 output (batch: 50% off)
- **GPT-4o**: $2.50 input / $10 output (batch: 50% off)
- **GPT-4o-mini**: $0.15 input / $0.60 output (batch: 50% off)
- **o3**: $15 input / $60 output
- **o4-mini**: $3 input / $12 output
- **GPT-3.5-turbo**: $0.50 input / $1.50 output (batch: 50% off)

### Token Counting
```python
import tiktoken

# For GPT-4.1 models
encoding = tiktoken.encoding_for_model("gpt-4")  # cl100k_base
tokens = encoding.encode("Your text here")

# For GPT-4o models
encoding = tiktoken.get_encoding("o200k_base")
tokens = encoding.encode("Your text here")

print(f"Token count: {len(tokens)}")
```

---

## Google (Gemini)

### Latest Models (July 2025)
- **Gemini 2.5 Pro** - Most capable model, 2M context
- **Gemini 2.5 Flash** - Ultra-fast, #2 on LMarena, 1M context, 22% efficiency gains
- **Gemini 2.0 Flash** - Previous generation, budget option
- **Gemini Flash-8B** - Experimental, 0.37s latency

### API Features
- **Batch Processing**: Via Vertex AI (50% discount)
- **Streaming**: Yes
- **Function Calling**: Yes
- **Vision**: Yes
- **Max Context**: 2M tokens (Pro), 1M tokens (Flash)
- **Output Limit**: 8192 tokens
- **Tokenizer**: SentencePiece-based (~4 characters per token)
- **Speed**: Flash models optimized for >100 tok/s performance

### Batch Processing (Vertex AI)
```bash
# Requires Google Cloud setup
gcloud ai models batch-predict \
  --model=gemini-2-5-flash \
  --input-format=jsonl \
  --gcs-source=gs://bucket/input.jsonl \
  --gcs-destination=gs://bucket/output/
```

### Pricing (per 1K tokens)
- **Gemini 2.5 Pro**: $0.00125 input / $0.005 output
- **Gemini 2.5 Flash**: $0.00001875 input / $0.000075 output
- **Gemini 2.0 Flash**: $0.000015 input / $0.00006 output
- **Batch pricing**: 50% discount for non-real-time requests

### Token Counting
```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
# For speed-critical applications
model = genai.GenerativeModel('gemini-2.5-flash')
# For maximum capability
# model = genai.GenerativeModel('gemini-2.5-pro')

# Count tokens
response = model.count_tokens("Your text here")
print(f"Token count: {response.total_tokens}")

# Note: A token is equivalent to about 4 characters for Gemini models
# 100 tokens are about 60-80 English words
```

---

## xAI (Grok)

### Latest Models (July 2025)
- **Grok 4** - Latest flagship, 256K context
- **Grok 4 Heavy** - Enhanced performance variant
- **Grok 3** - Previous flagship, 131K context
- **Grok 3 Mini** - Efficient variant
- **Grok 2** - Previous generation, excellent safety
- **Grok 2 Mini** - Lightweight version

### API Features
- **Batch Processing**: Not available
- **Streaming**: Yes
- **Function Calling**: Limited
- **Vision**: No
- **Max Context**: 256K tokens (Grok 4), 131K tokens (others)
- **Output Limit**: 8192 tokens
- **Tokenizer**: GPT-2 based (tiktoken compatible)
- **Live Search**: $25 per 1,000 sources used

### API Access
```python
# Currently uses OpenAI-compatible endpoint
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"
)
```

### Pricing (per 1M tokens)
- **Grok 4**: $15 input / $75 output
- **Grok 4 Heavy**: $20 input / $100 output
- **Grok 3**: $3 input / $15 output
- **Grok 3 Mini**: $0.30 input / $0.50 output
- **Grok 2**: $2 input / $10 output
- **Grok 2 Mini**: $0.50 input / $2 output

### Token Counting
```python
import tiktoken

# xAI uses similar tokenizer to OpenAI
encoding = tiktoken.encoding_for_model("gpt-4")
tokens = encoding.encode("Your text here")
print(f"Token count: {len(tokens)}")
```

---

## Batch Processing Comparison

| Provider | Batch API | Discount | Turnaround | Min Batch Size |
|----------|-----------|----------|------------|----------------|
| OpenAI | ✅ Native | 50% | 24 hours | No minimum |
| Anthropic | ✅ Native | None yet | 24 hours | No minimum |
| Google | ✅ Vertex AI | 50-96% | 24 hours | 100 requests |
| xAI | ❌ None | N/A | N/A | N/A |

### Batch Processing Best Practices

1. **OpenAI**:
   - Use JSONL format with custom_id for each request
   - Maximum 50,000 requests per batch
   - Auto-retry failed requests
   - Results include token usage per request

2. **Anthropic**:
   - Recently launched, still stabilizing
   - Supports up to 10,000 requests per batch
   - No discount yet but expected soon
   - Built-in result streaming

3. **Google (Vertex AI)**:
   - Requires GCS bucket setup
   - Best discounts but more complex setup
   - Regional pricing variations
   - Supports BigQuery integration

---

## Cost Analysis

### For 1000 Safety Questions (6 interactions each = 6000 requests)

**Ultra Budget & Fast (Under $0.50)**:
- Gemini 2.0 Flash (batch): ~$0.09
- Gemini 2.5 Flash (batch): ~$0.11 - **Best speed/quality/price**
- Grok 3 Mini: ~$0.30

**Budget Option (Under $1)**:
- GPT-4.1-nano (batch): ~$0.45
- Grok 2 Mini: ~$0.60
- GPT-4o-mini (batch): ~$0.75

**Balanced Option ($1-5)**:
- GPT-4.1-mini (batch): ~$1.08
- Claude Haiku 3.5: ~$1.50
- Grok 2: ~$3.60

**Premium Option ($5-20)**:
- Gemini 2.5 Pro (batch): ~$7.50
- GPT-4.1 (batch): ~$9.00
- Claude Sonnet 4: ~$9.00
- Grok 3: ~$9.00

**Enterprise Option ($20+)**:
- o4-mini: ~$18.00
- Claude Opus 4: ~$45.00
- o3: ~$90.00
- Grok 4: ~$90.00
- Grok 4 Heavy: ~$120.00

---

## API Limits & Rate Limiting

### Anthropic
- **Rate Limits**: Tier-based (Tier 1: 50 RPM, Tier 5: 4000 RPM)
- **Token Limits**: 400K TPM to 200M TPM based on tier
- **Batch Limits**: 10,000 requests per batch

### OpenAI
- **Rate Limits**: Model-specific (3-500 RPM)
- **Token Limits**: 10K-10M TPM based on tier
- **Batch Limits**: 50,000 requests per batch

### Google
- **Rate Limits**: 300 RPM for most models
- **Token Limits**: No hard limit, pay-as-you-go
- **Batch Limits**: Unlimited with Vertex AI

### xAI
- **Rate Limits**: 60 RPM standard
- **Token Limits**: 100K TPM
- **Batch Limits**: N/A

---

## Quick Start Commands

### Test API Connectivity
```bash
python tests/test_api_connectivity.py --provider all
```

### Create Batch Jobs
```bash
# OpenAI
python src/batch/batch_creator.py --provider openai --model gpt-4.1-mini

# Claude
python src/batch/batch_creator.py --provider claude --model claude-sonnet-4

# Gemini (requires GCP setup)
./scripts/run_gemini_batch.sh
```

### Monitor Batch Status
```bash
python scripts/batch_benchmark.py status
```

### Process Results
```bash
python src/batch/batch_processor.py batch_results.jsonl
```

---

## Token Counting Reference

### Quick Token Estimation
```python
def estimate_tokens(text, model_family):
    char_count = len(text)
    
    if "gemini" in model_family:
        return char_count / 4  # ~4 chars per token
    elif "claude" in model_family:
        return char_count / 3.5  # ~3.5 chars per token
    else:  # OpenAI, xAI
        return char_count / 4  # ~4 chars per token
```

### Cost Calculator
```python
def calculate_cost(input_tokens, output_tokens, model):
    costs = {
        "gpt-4.1": (5, 15),
        "gpt-4.1-mini": (0.6, 1.8),
        "claude-opus-4": (15, 75),
        "claude-sonnet-4": (3, 15),
        "grok-4": (15, 75),
        "gemini-2.5-pro": (1.25, 5),
    }
    
    input_cost, output_cost = costs.get(model, (0, 0))
    total = (input_tokens * input_cost + output_tokens * output_cost) / 1_000_000
    return f"${total:.4f}"
```

## Recommendations for SycoBench Testing

1. **For comprehensive testing**: Use batch APIs for OpenAI and Gemini to test all 1000 questions cost-effectively

2. **For quick validation**: Test with 10-20 questions using regular APIs across all providers

3. **For production comparison**: Focus on models that showed good safety scores previously (Opus 4, Grok 2)

4. **For cost optimization**: 
   - Use Gemini 2.0 Flash for ultra-low cost screening ($0.09 for 6K requests)
   - Use OpenAI batch API for all OpenAI models (50% savings)
   - Use Vertex AI for Gemini (50% discount)
   - Consider prompt caching for Anthropic (up to 90% savings)

5. **Model selection priority**:
   - Safety-critical: Claude Opus 4, Grok 4, o3
   - Balanced: Claude Sonnet 4, GPT-4.1, Grok 3
   - Speed-critical: Gemini 2.5 Flash (#2 overall, >100 tok/s), GPT-4.1-nano
   - Budget: Gemini 2.5 Flash, GPT-4.1-nano, Grok 3 Mini
   - Ultra-budget: Gemini 2.0 Flash