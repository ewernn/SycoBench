#!/usr/bin/env python3
"""Calculate Claude Sonnet 4 cost for unbatched API calls."""

# Claude Sonnet 4 pricing (regular API)
# From the code: Sonnet 4 costs $3/M input tokens, $15/M output tokens

questions = 1001
requests_per_question = 6  # Initial + 5 pressure levels
total_requests = questions * requests_per_question

# Token estimates (same as batch calculation)
est_input_tokens = total_requests * 100   # ~100 tokens per request
est_output_tokens = total_requests * 150  # ~150 tokens per response

# Calculate costs
input_cost = (est_input_tokens / 1_000_000) * 3.0
output_cost = (est_output_tokens / 1_000_000) * 15.0
total_cost = input_cost + output_cost

print('=== Claude Sonnet 4 Cost Analysis ===')
print('')
print('Regular API (unbatched):')
print('  Questions: {:,}'.format(questions))
print('  Total requests: {:,} (with pressure testing)'.format(total_requests))
print('  Estimated tokens: {:,} input, {:,} output'.format(est_input_tokens, est_output_tokens))
print('  Input cost: ${:.2f}'.format(input_cost))
print('  Output cost: ${:.2f}'.format(output_cost))
print('  Total cost: ${:.2f}'.format(total_cost))
print('')
print('Batch API (if it were available):')
print('  Cost with 50% discount: ${:.2f}'.format(total_cost * 0.5))
print('  Savings: ${:.2f}'.format(total_cost * 0.5))
print('')
print('Comparison with other models:')
print('  Claude 3.5 Sonnet: ${:.2f} (batch) or ${:.2f} (regular)'.format(7.66, 15.32))
print('  GPT-4.1-mini: ${:.2f} (batch) or ${:.2f} (regular)'.format(0.84, 1.68))
print('  Gemini 2.5 Flash: ${:.2f} (batch)'.format(0.26))