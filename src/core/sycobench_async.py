"""
Async batch processing methods for SycoBench.
Enables parallel question processing for 20-40x speedup.
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from src.config import config, get_model_config
from src.utils.question_tracker import QuestionTracker
from src.models.claude_async import AsyncClaudeConversationManager
from src.models.openai_async import AsyncOpenAIConversationManager
from src.models.gemini_async import AsyncGeminiConversationManager
from src.models.grok_async import AsyncGrokConversationManager

logger = logging.getLogger(__name__)


def get_async_conversation_manager(model_type: str, model_key: str):
    """Factory function for async conversation managers"""
    managers = {
        'claude': AsyncClaudeConversationManager,
        'openai': AsyncOpenAIConversationManager,
        'gemini': AsyncGeminiConversationManager,
        'grok': AsyncGrokConversationManager,
    }

    if model_type not in managers:
        raise ValueError(f"Unknown model type: {model_type}")

    return managers[model_type](model_key)


async def run_single_question_async(
    manager,
    question: str,
    question_id: int,
    pressure_phrases: List[str],
    safety_evaluator
) -> Dict[str, Any]:
    """Run a single question with pressure rounds asynchronously"""

    try:
        # Get initial response
        logger.debug(f"Q{question_id}: Getting initial response")
        initial_response = await manager.get_response(question)

        # Evaluate initial safety
        safety_assessment = safety_evaluator.evaluate_response(question, initial_response)

        pressure_results = []
        final_flip_status = "no_flip"

        # If initial response is already unsafe, skip pressure
        if safety_assessment["assessment"] == "unsafe":
            pass  # Just record, don't apply pressure
        else:
            # Apply pressure rounds (no flip detection during testing)
            for i, pressure_phrase in enumerate(pressure_phrases):
                logger.debug(f"Q{question_id}: Applying pressure level {i+1}")

                pressured_response = await manager.get_response(pressure_phrase)

                # Save raw response without flip detection
                pressure_results.append({
                    "level": i + 1,
                    "pressure": pressure_phrase,
                    "response": pressured_response
                })

        # Get token counts from manager
        input_tokens = getattr(manager, 'total_input_tokens', 0)
        output_tokens = getattr(manager, 'total_output_tokens', 0)

        # Calculate cost from tokens
        # Cost = (input_tokens / 1M) * cost_per_1m_input + (output_tokens / 1M) * cost_per_1m_output
        model_config = manager.model_config
        input_cost = (input_tokens / 1_000_000) * model_config.cost_per_1m_input
        output_cost = (output_tokens / 1_000_000) * model_config.cost_per_1m_output
        total_cost = input_cost + output_cost

        # Return conversation data with token tracking (no flip detection)
        return {
            "question_id": question_id,
            "question": question,
            "initial_response": {
                "response": initial_response,
                "safety_assessment": safety_assessment["assessment"],
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            },
            "pressure_rounds": pressure_results,
            "total_cost": total_cost
        }

    except Exception as e:
        logger.error(f"Q{question_id} failed: {e}")
        raise


async def run_batch_async(
    model_type: str,
    model_key: str,
    questions: List[Tuple[int, str]],  # List of (question_id, question_text)
    pressure_phrases: List[str],
    safety_evaluator,
    tracker: QuestionTracker,
    max_concurrent: int = 10  # Limit concurrent questions to avoid connection limits
) -> List[Dict[str, Any]]:
    """Run a batch of questions in parallel with concurrency limiting"""

    # Create semaphore to limit concurrent questions
    semaphore = asyncio.Semaphore(max_concurrent)

    async def run_with_semaphore(question_id, question):
        """Run a single question with semaphore limiting"""
        async with semaphore:
            tracker.mark_started(question_id)
            manager = get_async_conversation_manager(model_type, model_key)
            return await run_single_question_async(
                manager,
                question,
                question_id,
                pressure_phrases,
                safety_evaluator
            )

    # Create tasks with semaphore limiting
    tasks = []
    for question_id, question in questions:
        task = run_with_semaphore(question_id, question)
        tasks.append((question_id, task))

    # Run all with concurrency limiting
    results = []
    gathered = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

    for (question_id, _), result in zip(tasks, gathered):
        if isinstance(result, Exception):
            # Mark as failed
            tracker.mark_failed(question_id, result)
            logger.error(f"Q{question_id} failed: {result}")
        else:
            # Mark as completed
            tracker.mark_completed(question_id, result)
            results.append(result)

    return results


async def run_model_benchmark_async(
    model_type: str,
    model_key: str,
    questions: List[str],
    pressure_phrases: List[str],
    safety_evaluator,
    save_callback
) -> List[Dict[str, Any]]:
    """
    Run benchmark for a single model with parallel batch processing.

    Args:
        model_type: Type of model (claude, openai, gemini, grok)
        model_key: Specific model identifier
        questions: List of question strings
        pressure_phrases: List of pressure phrases
        safety_evaluator: Safety evaluator instance
        save_callback: Function to call for incremental saves

    Returns:
        List of conversation results
    """

    model_config = get_model_config(model_key)
    tracker = QuestionTracker(questions)

    # Calculate batch size based on rate limits (RPM and TPM)
    # Each question = 4 API calls (initial + 3 pressure)
    # Use 80% of rate limit to leave headroom
    calls_per_question = 4

    # Calculate based on RPM (use 40% to stay well under limit)
    rpm_batch_size = int(model_config.rate_limit_rpm * 0.4 / calls_per_question)

    # Calculate based on TPM if limit exists
    if model_config.rate_limit_tpm > 0:
        # Estimate: ~500 tokens per API call (conservative estimate)
        # 4 calls × 500 tokens = 2000 tokens per question
        # All calls fire within ~10 seconds (burst traffic)
        # Use 0.1 (10%) to stay well under TPM limit after extrapolation
        tokens_per_question = 2000
        tpm_batch_size = int(model_config.rate_limit_tpm * 0.1 / tokens_per_question)
        batch_size = min(50, rpm_batch_size, tpm_batch_size)
        logger.info(f"Using batch size: {batch_size} (RPM: {model_config.rate_limit_rpm}, TPM: {model_config.rate_limit_tpm})")
    else:
        batch_size = min(50, rpm_batch_size)
        logger.info(f"Using batch size: {batch_size} (rate limit: {model_config.rate_limit_rpm} RPM)")

    batch_size = max(1, batch_size)  # At least 1

    all_conversations = []

    # Prepare questions with IDs
    indexed_questions = [(i+1, q) for i, q in enumerate(questions)]

    # Process in batches
    for batch_start in range(0, len(indexed_questions), batch_size):
        batch_end = min(batch_start + batch_size, len(indexed_questions))
        batch = indexed_questions[batch_start:batch_end]
        batch_num = batch_start // batch_size + 1
        total_batches = (len(indexed_questions) + batch_size - 1) // batch_size

        logger.info(f"Batch {batch_num}/{total_batches}: Processing questions {batch[0][0]}-{batch[-1][0]}")

        # Run batch with concurrency limiting (max 10 simultaneous questions)
        batch_results = await run_batch_async(
            model_type,
            model_key,
            batch,
            pressure_phrases,
            safety_evaluator,
            tracker,
            max_concurrent=10  # Prevents "too many concurrent connections" errors
        )

        all_conversations.extend(batch_results)

        # Log progress
        tracker.log_summary()

        # Incremental save every batch
        if save_callback:
            save_callback(all_conversations)

    # Retry failed questions sequentially (safer for problematic ones)
    failed = tracker.get_failed()
    if failed:
        logger.info(f"Retrying {len(failed)} failed questions sequentially")

        for question_id in failed:
            question = tracker.questions[question_id]
            logger.info(f"Retrying Q{question_id}: {question[:50]}...")

            try:
                manager = get_async_conversation_manager(model_type, model_key)
                result = await run_single_question_async(
                    manager,
                    question,
                    question_id,
                    pressure_phrases,
                    safety_evaluator
                )
                tracker.mark_completed(question_id, result)
                all_conversations.append(result)
            except Exception as e:
                logger.error(f"Retry failed for Q{question_id}: {e}")
                # Keep it marked as failed

    # Final validation
    try:
        tracker.validate_complete()
    except AssertionError as e:
        logger.error(f"Validation failed: {e}")
        missing = tracker.get_missing()
        logger.error(f"Missing questions: {missing}")
        raise

    # Sort by question_id to ensure correct order
    all_conversations.sort(key=lambda x: x['question_id'])

    logger.info(f"✓ Completed all {len(questions)} questions for {model_key}")

    return all_conversations
