# SycoBench Cost Comparison: Regular API vs Batch Processing

## Executive Summary

Batch processing offers **50-96% cost savings** compared to regular API calls for large-scale safety testing.

## Cost Breakdown: 1,000 Questions with Full Pressure Testing

Each test involves:
- 1,000 safety questions
- 6 interactions per question (initial + 5 pressure levels)
- Total: 6,000 API calls

### OpenAI Models

| Model | Regular API Cost | Batch API Cost | Savings | Time (Regular) | Time (Batch) |
|-------|-----------------|----------------|---------|----------------|--------------|
| **gpt-4.1-nano** | $1.00 | $0.50 | **50%** | ~17 hours* | 0.5-2 hours |
| **gpt-4.1-mini** | $4.00 | $2.00 | **50%** | ~17 hours* | 0.5-2 hours |
| **gpt-4.1** | $10.00 | $5.00 | **50%** | ~17 hours* | 0.5-2 hours |
| **gpt-4o-mini** | $1.50 | $0.75 | **50%** | ~33 hours* | 0.5-2 hours |
| **gpt-3.5-turbo** | $3.00 | $1.50 | **50%** | ~33 hours* | 0.5-2 hours |

*Due to rate limits: 3-10 RPM depending on model

### Google Gemini Models

| Model | Regular API Cost | Batch API Cost | Savings | Time (Regular) | Time (Batch) |
|-------|-----------------|----------------|---------|----------------|--------------|
| **gemini-2.5-flash** | ~$15.00** | $0.37 | **96%** | ~6.7 hours** | 0.25-1 hour |
| **gemini-2.5-pro** | ~$75.00** | $12.50 | **83%** | ~6.7 hours** | 0.25-1 hour |

**Includes rate limiting delays (15 RPM)

### Anthropic Claude Models

| Model | Regular API Cost | Batch API Cost | Savings | Time (Regular) | Time (Batch) |
|-------|-----------------|----------------|---------|----------------|--------------|
| **claude-haiku-3.5** | $5.40 | Not available | - | ~2 hours | - |
| **claude-sonnet-4** | $21.60 | Not available | - | ~2 hours | - |
| **claude-opus-4** | $108.00 | Not available | - | ~2 hours | - |

Note: Anthropic batch API announced but not yet available

### xAI Grok Models

| Model | Regular API Cost | Batch API Cost | Savings | Time (Regular) | Time (Batch) |
|-------|-----------------|----------------|---------|----------------|--------------|
| **grok-3-mini** | $2.10 | Not available | - | ~1 hour | - |
| **grok-3** | $21.60 | Not available | - | ~1 hour | - |

## Cost Calculation Details

### Regular API Costs Include:
- Token costs (input + output)
- No discounts
- Must respect rate limits

### Batch API Benefits:
- **50% discount** (OpenAI)
- **Flat low pricing** (Gemini)
- **No rate limit delays**
- **Automatic retries**
- **Higher throughput**

## Example Scenarios

### Scenario 1: Budget Testing ($1)
**Regular API:** 
- Can test ~160 questions with gpt-4.1-nano
- Takes ~3 hours with rate limits

**Batch API:**
- Can test 1,000 questions with gpt-4.1-nano ($0.50)
- Plus 1,000 questions with gemini-2.5-flash ($0.37)
- Total: 2,000 questions for $0.87

### Scenario 2: Comprehensive Testing ($10)
**Regular API:**
- 1,000 questions with gpt-4.1-mini: $4.00
- 370 questions with claude-haiku-3.5: $2.00
- 280 questions with grok-3-mini: $0.60
- Total: 1,650 questions

**Batch API:**
- 1,000 questions each with:
  - gpt-4.1-nano: $0.50
  - gpt-4.1-mini: $2.00
  - gpt-4o-mini: $0.75
  - gemini-2.5-flash: $0.37
  - gemini-2.5-pro: $12.50 (skip if over budget)
- Total: 4,000-5,000 questions for same price

### Scenario 3: Time-Sensitive Testing
**Regular API:**
- Limited by rate limits
- 6,000 calls at 3 RPM = 33 hours
- 6,000 calls at 15 RPM = 6.7 hours

**Batch API:**
- All providers complete within 2 hours
- Most finish in 30-60 minutes
- Process in parallel

## ROI Analysis

### For 10,000 Question Study:

**Regular API Total Cost:**
- OpenAI (gpt-4.1-mini): $40.00
- Gemini (2.5-flash): $150.00
- Claude (haiku-3.5): $54.00
- **Total: $244.00**

**Batch API Total Cost:**
- OpenAI (gpt-4.1-mini): $20.00
- Gemini (2.5-flash): $3.70
- Claude: Not available
- **Total: $23.70**

**Savings: $220.30 (90%)**

## Recommendations

1. **For Budget-Conscious Testing:**
   - Use Gemini 2.5 Flash batch ($0.37 per 1,000 questions)
   - 96% cheaper than regular API

2. **For Quick Results:**
   - Use batch APIs to avoid rate limit delays
   - Complete in hours instead of days

3. **For Comprehensive Studies:**
   - Combine multiple batch jobs
   - Test 10x more questions for same budget

4. **For Research Papers:**
   - Batch APIs enable larger sample sizes
   - More statistically significant results
   - Lower cost per data point

## When to Use Each

### Use Regular API When:
- Testing < 10 questions
- Need immediate interactive results
- Debugging or development
- Real-time applications

### Use Batch API When:
- Testing > 100 questions
- Cost is a concern
- Time window of 2-24 hours is acceptable
- Running evaluation suites
- Generating research datasets

## Bottom Line

For SycoBench's use case of testing AI safety with 1,000+ questions:
- **Batch APIs save 50-96% on costs**
- **Complete 10-100x faster** (no rate limit delays)
- **Enable larger, more comprehensive studies**
- **Reduce cost from $244 to $24 for 10k questions**

The only tradeoff is waiting 0.5-2 hours instead of getting immediate results.