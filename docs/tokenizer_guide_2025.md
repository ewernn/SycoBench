# Tokenizer Guide for AI Models (July 2025)

*Last Updated: July 2025*

This guide provides comprehensive information about tokenizers used by different AI model providers, including token counting methods, cost optimization strategies, and practical examples.

## Table of Contents
1. [Overview](#overview)
2. [Provider-Specific Tokenizers](#provider-specific-tokenizers)
3. [Token Counting Implementation](#token-counting-implementation)
4. [Cost Optimization Strategies](#cost-optimization-strategies)
5. [Token Estimation Tools](#token-estimation-tools)
6. [Batch Processing Considerations](#batch-processing-considerations)

---

## Overview

### What is a Token?
A token is the basic unit of text that language models process. Different models use different tokenization methods:
- **English text**: ~3.5-4 characters per token
- **Code**: ~2-3 characters per token (more tokens due to syntax)
- **Non-English text**: Can vary significantly (Chinese/Japanese: ~1-2 characters per token)

### Why Token Counting Matters
1. **Cost calculation**: API pricing is per token
2. **Context limits**: Models have maximum token windows
3. **Output planning**: Ensure responses fit within limits
4. **Batch optimization**: Maximize efficiency within constraints

---

## Provider-Specific Tokenizers

### Google Gemini
**Tokenizer**: SentencePiece-based
- ~4 characters per token for English
- 100 tokens ≈ 60-80 English words

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-pro')

# Count tokens for input
text = "Is it safe to mix bleach and ammonia?"
response = model.count_tokens(text)
print(f"Token count: {response.total_tokens}")

# Count tokens for conversation
messages = [
    {"role": "user", "parts": [{"text": "Hello"}]},
    {"role": "model", "parts": [{"text": "Hi there!"}]}
]
response = model.count_tokens(messages)
print(f"Conversation tokens: {response.total_tokens}")
```

### xAI (Grok)
**Tokenizer**: GPT-2 based (tiktoken compatible)
- Similar to OpenAI's tokenization
- ~4 characters per token

```python
import tiktoken

# xAI uses GPT-2 based tokenizer
encoding = tiktoken.encoding_for_model("gpt-4")
text = "Is it safe to mix bleach and ammonia?"
tokens = encoding.encode(text)
print(f"Token count: {len(tokens)}")

# Decode tokens to see how text is split
for i, token in enumerate(tokens):
    print(f"Token {i}: '{encoding.decode([token])}'")
```

### OpenAI
**Tokenizers**: 
- cl100k_base: GPT-4, GPT-4.1 models
- o200k_base: GPT-4o models (more efficient for non-English)

```python
import tiktoken

# For GPT-4.1 models
encoding_cl100k = tiktoken.encoding_for_model("gpt-4")
text = "Is it safe to mix bleach and ammonia?"
tokens = encoding_cl100k.encode(text)
print(f"cl100k_base tokens: {len(tokens)}")

# For GPT-4o models
encoding_o200k = tiktoken.get_encoding("o200k_base")
tokens = encoding_o200k.encode(text)
print(f"o200k_base tokens: {len(tokens)}")

# Compare tokenization efficiency
multilingual_text = "こんにちは世界" # "Hello world" in Japanese
cl100k_tokens = len(encoding_cl100k.encode(multilingual_text))
o200k_tokens = len(encoding_o200k.encode(multilingual_text))
print(f"Japanese text - cl100k: {cl100k_tokens}, o200k: {o200k_tokens}")
```

### Anthropic (Claude)
**Tokenizer**: Proprietary Claude tokenizer
- ~3.5 characters per token for English
- More efficient than GPT tokenizers for some languages

```python
import anthropic

client = anthropic.Anthropic(api_key="YOUR_KEY")

# Basic token counting
text = "Is it safe to mix bleach and ammonia?"
token_count = client.count_tokens(text)
print(f"Token count: {token_count}")

# Count tokens for messages format
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
]
# Note: Anthropic's API handles token counting internally
# Estimate: ~3.5 characters per token
estimated_tokens = sum(len(m["content"]) for m in messages) / 3.5
print(f"Estimated tokens: {estimated_tokens:.0f}")
```

---

## Token Counting Implementation

### Universal Token Counter
```python
class TokenCounter:
    def __init__(self):
        self.encodings = {}
        self._init_encodings()
    
    def _init_encodings(self):
        try:
            import tiktoken
            self.encodings['cl100k_base'] = tiktoken.encoding_for_model("gpt-4")
            self.encodings['o200k_base'] = tiktoken.get_encoding("o200k_base")
        except ImportError:
            pass
    
    def count_tokens(self, text, model):
        """Count tokens for any model."""
        if model.startswith("gpt-4.1"):
            return len(self.encodings['cl100k_base'].encode(text))
        elif model.startswith("gpt-4o"):
            return len(self.encodings['o200k_base'].encode(text))
        elif model.startswith("grok"):
            return len(self.encodings['cl100k_base'].encode(text))
        elif model.startswith("claude"):
            return len(text) / 3.5  # Estimate
        elif model.startswith("gemini"):
            return len(text) / 4    # Estimate
        else:
            return len(text) / 4    # Default estimate
    
    def estimate_cost(self, input_tokens, output_tokens, model):
        """Calculate cost based on token counts."""
        costs = {
            # Model: (input_per_1M, output_per_1M)
            "gpt-4.1": (5, 15),
            "gpt-4.1-mini": (0.6, 1.8),
            "gpt-4.1-nano": (0.15, 0.45),
            "gpt-4o": (2.5, 10),
            "gpt-4o-mini": (0.15, 0.6),
            "claude-opus-4": (15, 75),
            "claude-sonnet-4": (3, 15),
            "claude-haiku-3.5": (0.25, 1.25),
            "grok-4": (15, 75),
            "grok-3": (3, 15),
            "grok-3-mini": (0.3, 0.5),
            "gemini-2.5-pro": (1.25, 5),
            "gemini-2.5-flash": (0.01875, 0.075),
            "o3": (15, 60),
            "o4-mini": (3, 12)
        }
        
        if model in costs:
            input_cost, output_cost = costs[model]
            total = (input_tokens * input_cost + output_tokens * output_cost) / 1_000_000
            return total
        return 0

# Usage
counter = TokenCounter()
text = "Is it safe to mix bleach and ammonia?"
tokens = counter.count_tokens(text, "gpt-4.1-mini")
cost = counter.estimate_cost(tokens, tokens * 2, "gpt-4.1-mini")
print(f"Tokens: {tokens}, Estimated cost: ${cost:.4f}")
```

---

## Cost Optimization Strategies

### 1. Model Selection by Token Efficiency
```python
def compare_models_for_text(text, expected_output_ratio=2):
    """Compare cost efficiency across models."""
    counter = TokenCounter()
    
    models = [
        "gemini-2.0-flash",
        "gemini-2.5-flash", 
        "grok-3-mini",
        "gpt-4.1-nano",
        "claude-haiku-3.5"
    ]
    
    results = []
    for model in models:
        input_tokens = counter.count_tokens(text, model)
        output_tokens = input_tokens * expected_output_ratio
        cost = counter.estimate_cost(input_tokens, output_tokens, model)
        results.append({
            "model": model,
            "tokens": input_tokens + output_tokens,
            "cost": cost
        })
    
    # Sort by cost
    results.sort(key=lambda x: x['cost'])
    return results
```

### 2. Batch Optimization
```python
def optimize_batch_size(questions, model, max_tokens_per_request=4000):
    """Optimize batch sizes to maximize API efficiency."""
    counter = TokenCounter()
    batches = []
    current_batch = []
    current_tokens = 0
    
    for question in questions:
        tokens = counter.count_tokens(question, model)
        # Add overhead for response
        total_tokens = tokens + (tokens * 2)  # Assume 2x for response
        
        if current_tokens + total_tokens > max_tokens_per_request:
            batches.append(current_batch)
            current_batch = [question]
            current_tokens = total_tokens
        else:
            current_batch.append(question)
            current_tokens += total_tokens
    
    if current_batch:
        batches.append(current_batch)
    
    return batches
```

### 3. Prompt Optimization
```python
def optimize_prompt(base_prompt, model):
    """Optimize prompts for token efficiency."""
    counter = TokenCounter()
    
    # Original verbose prompt
    verbose = f"""
    You are a helpful AI assistant. Please carefully consider the following 
    question and provide a thoughtful, accurate response. Make sure to think 
    about safety implications.
    
    Question: {base_prompt}
    
    Please provide your response below:
    """
    
    # Optimized concise prompt
    concise = f"Safety question: {base_prompt}\nAnswer:"
    
    verbose_tokens = counter.count_tokens(verbose, model)
    concise_tokens = counter.count_tokens(concise, model)
    
    savings = (verbose_tokens - concise_tokens) / verbose_tokens * 100
    print(f"Token savings: {savings:.1f}% ({verbose_tokens} -> {concise_tokens})")
    
    return concise
```

---

## Token Estimation Tools

### Quick Reference Table
| Text Type | Tokens per 1000 chars | Best Model for Efficiency |
|-----------|---------------------|--------------------------|
| English prose | ~250 | Any (similar efficiency) |
| Code | ~330 | GPT-4o (o200k_base) |
| Chinese/Japanese | ~500 | GPT-4o (o200k_base) |
| Mixed multilingual | ~300 | GPT-4o or Claude |

### Estimation Functions
```python
def quick_estimate_tokens(text, language="english"):
    """Quick token estimation without loading tokenizers."""
    char_count = len(text)
    
    estimates = {
        "english": char_count / 4,
        "code": char_count / 3,
        "chinese": char_count / 2,
        "japanese": char_count / 2,
        "mixed": char_count / 3.5
    }
    
    return int(estimates.get(language, char_count / 4))

def estimate_conversation_tokens(messages):
    """Estimate tokens for a full conversation."""
    total = 0
    
    # Add message formatting overhead (~4 tokens per message)
    total += len(messages) * 4
    
    # Add content tokens
    for message in messages:
        content = message.get("content", "")
        total += quick_estimate_tokens(content)
    
    return total
```

---

## Batch Processing Considerations

### Token Limits by Provider
| Provider | Max Tokens per Request | Max Tokens per Batch |
|----------|----------------------|---------------------|
| OpenAI | 128K (most models) | 50M (50K requests) |
| Anthropic | 200K | 10M (10K requests) |
| Google | 1-2M | Unlimited |
| xAI | 131-256K | N/A |

### Batch File Optimization
```python
def create_optimized_batch_file(questions, model, provider):
    """Create batch file optimized for token limits."""
    counter = TokenCounter()
    
    if provider == "openai":
        max_tokens = 128000
        max_requests = 50000
    elif provider == "anthropic":
        max_tokens = 200000
        max_requests = 10000
    else:
        max_tokens = 1000000
        max_requests = float('inf')
    
    batch_requests = []
    
    for i, question in enumerate(questions[:max_requests]):
        tokens = counter.count_tokens(question, model)
        
        if tokens > max_tokens * 0.5:  # Leave room for response
            # Split long questions
            chunks = [question[i:i+1000] for i in range(0, len(question), 1000)]
            for j, chunk in enumerate(chunks):
                batch_requests.append({
                    "custom_id": f"q_{i}_chunk_{j}",
                    "question": chunk
                })
        else:
            batch_requests.append({
                "custom_id": f"q_{i}",
                "question": question
            })
    
    return batch_requests
```

### Cost Comparison Tool
```python
def compare_batch_costs(num_questions=1000, avg_question_length=100):
    """Compare costs across providers for batch processing."""
    counter = TokenCounter()
    
    # Estimate tokens
    sample_question = "a" * avg_question_length
    
    providers = {
        "OpenAI": {
            "models": ["gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1"],
            "batch_discount": 0.5
        },
        "Anthropic": {
            "models": ["claude-haiku-3.5", "claude-sonnet-4", "claude-opus-4"],
            "batch_discount": 0.5
        },
        "Google": {
            "models": ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"],
            "batch_discount": 0.5
        },
        "xAI": {
            "models": ["grok-3-mini", "grok-3", "grok-4"],
            "batch_discount": 0  # No batch API
        }
    }
    
    results = []
    
    for provider, config in providers.items():
        for model in config["models"]:
            input_tokens = counter.count_tokens(sample_question, model) * num_questions * 6  # 6 interactions
            output_tokens = input_tokens * 2  # Estimate 2x output
            
            base_cost = counter.estimate_cost(input_tokens, output_tokens, model)
            batch_cost = base_cost * (1 - config["batch_discount"])
            
            results.append({
                "provider": provider,
                "model": model,
                "base_cost": base_cost,
                "batch_cost": batch_cost,
                "savings": base_cost - batch_cost
            })
    
    # Sort by batch cost
    results.sort(key=lambda x: x['batch_cost'])
    
    print(f"Cost comparison for {num_questions} questions (6 interactions each):\n")
    print(f"{'Model':<20} {'Regular Cost':<12} {'Batch Cost':<12} {'Savings':<10}")
    print("-" * 60)
    
    for r in results:
        print(f"{r['model']:<20} ${r['base_cost']:<11.2f} ${r['batch_cost']:<11.2f} ${r['savings']:<9.2f}")
    
    return results

# Run comparison
compare_batch_costs(1000, 100)
```

---

## Best Practices

1. **Always count tokens before sending requests** to avoid unexpected costs
2. **Use batch APIs when available** for 50% cost savings
3. **Optimize prompts** to reduce token usage without losing clarity
4. **Cache tokenizer instances** to avoid repeated initialization
5. **Monitor token usage** in production to identify optimization opportunities
6. **Consider model-specific tokenizers** for accurate counting
7. **Test with small batches first** to verify token estimates

---

## Quick Reference

### Token Counting Libraries
```bash
# Install required libraries
pip install tiktoken          # OpenAI/xAI tokenizers
pip install google-generativeai  # Gemini token counting
pip install anthropic         # Claude token counting
```

### Environment Setup
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Set up API keys
os.environ["OPENAI_API_KEY"] = "your-key"
os.environ["ANTHROPIC_API_KEY"] = "your-key"
os.environ["GEMINI_API_KEY"] = "your-key"
os.environ["XAI_API_KEY"] = "your-key"
```

---

Remember: Token counts are estimates until actually processed by the API. Always add a buffer (10-20%) for safety when working near limits.