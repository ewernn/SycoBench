# API Parameters Guide for SycoBench

*Last Updated: September 29, 2025*

This document provides the exact API parameter requirements for each provider's Python SDK.

## Temperature Settings

**SycoBench uses `temperature=0.0` for all models** to ensure reproducible, deterministic results.

### Temperature Ranges by Provider
- **Gemini**: 0.0 to 2.0 (default: 1.0)
- **OpenAI**: 0.0 to 2.0 (default: 1.0)
- **Anthropic**: 0.0 to 1.0 (default: 1.0)
- **xAI/Grok**: 0.0 to 2.0 (follows OpenAI convention)

## Provider-Specific Parameters

### OpenAI (GPT-5, O-series)

```python
from openai import OpenAI

client = OpenAI(api_key='YOUR_API_KEY')

# GPT-5 models (gpt-5, gpt-5-mini, gpt-5-nano)
# WARNING: gpt-5-nano only supports temperature=1.0
response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[{"role": "user", "content": "Your prompt"}],
    temperature=1.0,                     # gpt-5-nano ONLY supports 1.0!
    max_completion_tokens=200            # NOT max_tokens!
)

# GPT-5 and GPT-5-mini support temperature=0.0
response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "Your prompt"}],
    temperature=0.0,                     # Supported for gpt-5 and gpt-5-mini
    max_completion_tokens=200
)

# O-series models (o3, o4-mini)
response = client.chat.completions.create(
    model="o3",
    messages=[{"role": "user", "content": "Your prompt"}],
    max_completion_tokens=200,           # NOT max_tokens!
    reasoning_effort="medium"             # Optional: low/medium/high
    # Note: o-series does NOT support temperature parameter
)

# Legacy models (if any)
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Your prompt"}],
    temperature=0.0,
    max_tokens=200                       # Old models use max_tokens
)
```

**Critical Notes:**
- ✅ GPT-5 models: Use `max_completion_tokens` (NOT `max_tokens`)
- ✅ O-series models: Use `max_completion_tokens`, no temperature support
- ⚠️ Using `max_tokens` with GPT-5 will cause error 400

### Anthropic (Claude)

```python
from anthropic import Anthropic

client = Anthropic(api_key='YOUR_API_KEY')

response = client.messages.create(
    model="claude-3-5-haiku-20241022",
    messages=[{"role": "user", "content": "Your prompt"}],
    temperature=0.0,                     # Range: 0.0 to 1.0
    max_tokens=200                       # Claude uses max_tokens
)

# For long operations (Opus/Sonnet 4.5)
with client.messages.stream(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "Your prompt"}],
    temperature=0.0,
    max_tokens=200
) as stream:
    for text in stream.text_stream:
        # Handle streaming response
```

**Critical Notes:**
- ✅ All Claude models use `max_tokens`
- ✅ Temperature range is 0.0 to 1.0 (not 2.0)
- ⚠️ Opus/Sonnet models require streaming for long operations

### Google Gemini

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')

response = client.models.generate_content(
    model='gemini-2.5-flash-lite',
    contents='Your prompt',
    config=types.GenerateContentConfig(
        temperature=0.0,                 # Range: 0.0 to 2.0
        max_output_tokens=200            # Gemini uses max_output_tokens
    )
)
```

**Critical Notes:**
- ✅ Gemini uses `max_output_tokens` (not max_tokens)
- ✅ Temperature must be set in the config object
- ✅ Contents can be string or structured format

### xAI (Grok)

```python
# Using OpenAI-compatible syntax (recommended)
from openai import OpenAI

client = OpenAI(
    api_key='YOUR_XAI_API_KEY',
    base_url="https://api.x.ai/v1"
)

response = client.chat.completions.create(
    model="grok-4-fast-non-reasoning",
    messages=[{"role": "user", "content": "Your prompt"}],
    temperature=0.0,                     # Range: 0.0 to 2.0
    max_tokens=200                       # Grok uses max_tokens
)
```

**Critical Notes:**
- ✅ Grok uses OpenAI-compatible API
- ✅ Uses `max_tokens` (not max_completion_tokens)
- ✅ Temperature range is 0.0 to 2.0

## Summary Table

| Provider | Token Parameter | Temperature Support | Temperature Range | Streaming Required |
|----------|-----------------|--------------------|--------------------|-------------------|
| GPT-5 | `max_completion_tokens` | ✅ Yes | 0.0 - 2.0 | No |
| O-series | `max_completion_tokens` | ❌ No | N/A | No |
| Claude | `max_tokens` | ✅ Yes | 0.0 - 1.0 | Opus/Sonnet only |
| Gemini | `max_output_tokens` | ✅ Yes | 0.0 - 2.0 | No |
| Grok | `max_tokens` | ✅ Yes | 0.0 - 2.0 | No |

## Common Errors and Solutions

### Error: "Unsupported parameter: 'max_tokens' is not supported"
**Provider:** OpenAI GPT-5
**Solution:** Use `max_completion_tokens` instead of `max_tokens`

### Error: "Streaming is required for operations that may take longer than 10 minutes"
**Provider:** Anthropic Claude (Opus/Sonnet)
**Solution:** Use streaming API with `client.messages.stream()`

### Error: "temperature must be between 0.0 and 1.0"
**Provider:** Anthropic Claude
**Solution:** Claude's temperature range is 0.0-1.0, not 0.0-2.0

### Error: "Missing key inputs argument"
**Provider:** Google Gemini
**Solution:** Ensure `api_key` is provided to `genai.Client()`

## SycoBench Implementation

SycoBench automatically handles these differences in `src/models/`:
- `openai_models.py`: Uses `max_completion_tokens` for GPT-5/O-series
- `claude.py`: Uses `max_tokens` and streaming for Opus/Sonnet
- `gemini.py`: Uses `max_output_tokens` in config
- `grok.py`: Uses OpenAI-compatible `max_tokens`

All models are configured with `temperature=0.0` (except O-series which doesn't support it) for reproducibility.