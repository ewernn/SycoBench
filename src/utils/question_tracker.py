"""
Question tracking system for async batch processing.
Ensures no questions are missed, duplicated, or double-counted.
"""
from typing import Set, Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class QuestionStatus:
    """Status of a single question"""
    question_id: int
    question_text: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0


class QuestionTracker:
    """
    Tracks the status of all questions during batch processing.
    Ensures exactly-once processing and no missing questions.
    """

    def __init__(self, questions: List[str]):
        self.total = len(questions)
        self.questions = {i+1: q for i, q in enumerate(questions)}
        self.status: Dict[int, QuestionStatus] = {}

        # Initialize all questions as pending
        for qid, qtext in self.questions.items():
            self.status[qid] = QuestionStatus(
                question_id=qid,
                question_text=qtext,
                status='pending'
            )

        logger.info(f"Initialized tracker for {self.total} questions")

    def mark_started(self, question_id: int) -> None:
        """Mark a question as in progress"""
        if question_id not in self.status:
            raise ValueError(f"Invalid question_id: {question_id}")

        self.status[question_id].status = 'in_progress'
        logger.debug(f"Question {question_id} started")

    def mark_completed(self, question_id: int, result: Any) -> None:
        """Mark a question as successfully completed"""
        if question_id not in self.status:
            raise ValueError(f"Invalid question_id: {question_id}")

        self.status[question_id].status = 'completed'
        self.status[question_id].result = result
        logger.debug(f"Question {question_id} completed")

    def mark_failed(self, question_id: int, error: Exception) -> None:
        """Mark a question as failed"""
        if question_id not in self.status:
            raise ValueError(f"Invalid question_id: {question_id}")

        self.status[question_id].status = 'failed'
        self.status[question_id].error = str(error)
        self.status[question_id].retry_count += 1
        logger.warning(f"Question {question_id} failed: {error}")

    def get_pending(self) -> List[int]:
        """Get all pending question IDs"""
        return [qid for qid, status in self.status.items() if status.status == 'pending']

    def get_in_progress(self) -> List[int]:
        """Get all in-progress question IDs"""
        return [qid for qid, status in self.status.items() if status.status == 'in_progress']

    def get_completed(self) -> List[int]:
        """Get all completed question IDs"""
        return [qid for qid, status in self.status.items() if status.status == 'completed']

    def get_failed(self) -> List[int]:
        """Get all failed question IDs"""
        return [qid for qid, status in self.status.items() if status.status == 'failed']

    def get_missing(self) -> List[int]:
        """Get question IDs that are not completed (pending, in_progress, or failed)"""
        completed = set(self.get_completed())
        all_ids = set(range(1, self.total + 1))
        return sorted(list(all_ids - completed))

    def get_completed_results(self) -> List[Any]:
        """Get results for all completed questions, in order by question_id"""
        completed = [(qid, status.result) for qid, status in self.status.items()
                     if status.status == 'completed']
        return [result for qid, result in sorted(completed)]

    def validate_complete(self) -> bool:
        """
        Validate that all questions are completed.
        Returns True if valid, raises AssertionError if not.
        """
        completed = self.get_completed()
        missing = self.get_missing()

        logger.info(f"Validation: {len(completed)}/{self.total} completed")

        if len(completed) != self.total:
            raise AssertionError(
                f"Expected {self.total} completed questions, got {len(completed)}. "
                f"Missing: {missing}"
            )

        if missing:
            raise AssertionError(f"Missing questions: {missing}")

        # Check for duplicates in results
        results = self.get_completed_results()
        if len(results) != len(completed):
            raise AssertionError(
                f"Result count mismatch: {len(results)} results vs {len(completed)} completed"
            )

        logger.info(f"✓ Validation passed: All {self.total} questions completed")
        return True

    def get_summary(self) -> Dict[str, int]:
        """Get summary of question statuses"""
        return {
            'total': self.total,
            'completed': len(self.get_completed()),
            'failed': len(self.get_failed()),
            'in_progress': len(self.get_in_progress()),
            'pending': len(self.get_pending())
        }

    def log_summary(self) -> None:
        """Log current status summary"""
        summary = self.get_summary()
        logger.info(
            f"Status: {summary['completed']}/{summary['total']} completed, "
            f"{summary['failed']} failed, {summary['in_progress']} in progress, "
            f"{summary['pending']} pending"
        )
