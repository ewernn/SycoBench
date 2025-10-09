import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from loguru import logger
from rich.logging import RichHandler
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn


# Create console for rich output
console = Console()


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    use_rich: bool = True
):
    """Setup logging configuration for SycoBench"""
    
    # Remove default loguru handler
    logger.remove()
    
    # Configure log format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Add console handler
    if use_rich:
        # Rich console handler for pretty output
        logger.add(
            sys.stderr,
            format=log_format,
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
    else:
        # Simple console handler
        logger.add(
            sys.stderr,
            format="{time} | {level} | {message}",
            level=log_level
        )
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",  # File gets all logs
            rotation="100 MB",
            retention="1 week",
            compression="zip"
        )
    
    # Configure standard library logging to use loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    # Setup standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # Silence noisy libraries
    noisy_loggers = [
        "urllib3", "requests", "httpx", "httpcore",
        # Silence Gemini AFC spam
        "google.genai", "google.genai.live", "google.genai.client",
        "google.ai", "google.ai.generativelanguage"
    ]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.ERROR)
    
    return logger


def create_progress_bar(description: str = "Processing"):
    """Create a rich progress bar for long operations"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
        transient=True
    )


class BenchmarkLogger:
    """Specialized logger for benchmark operations"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = datetime.utcnow()
        self.logger = logger.bind(test=test_name)
    
    def log_test_start(self, model: str, question: str):
        self.logger.info(
            f"Starting test",
            model=model,
            question=question[:50] + "..." if len(question) > 50 else question
        )
    
    def log_test_complete(self, model: str, result: str, duration: float):
        self.logger.success(
            f"Test completed",
            model=model,
            result=result,
            duration=f"{duration:.2f}s"
        )
    
    def log_pressure_applied(self, level: int, pressure: str):
        self.logger.debug(
            f"Applying pressure level {level}",
            pressure=pressure
        )
    
    def log_flip_detected(self, flip_type: str, level: int):
        if flip_type == "explicit_flip":
            self.logger.warning(
                f"Explicit flip detected at level {level}"
            )
        elif flip_type == "soft_flip":
            self.logger.info(
                f"Soft flip detected at level {level}"
            )
    
    def log_benchmark_summary(self, total_tests: int, duration: float, summary: dict):
        self.logger.success(
            f"Benchmark '{self.test_name}' completed",
            total_tests=total_tests,
            duration=f"{duration:.2f}s",
            summary=summary
        )
    
    def log_error(self, error: Exception, context: str):
        self.logger.error(
            f"Error in {context}",
            error_type=type(error).__name__,
            error_message=str(error)
        )


# Convenience functions
def log_model_info(model_name: str, model_config: dict):
    """Log model configuration info"""
    logger.info(
        f"Initialized model",
        model=model_name,
        context_window=model_config.get("context_window"),
        supports_thinking=model_config.get("supports_thinking", False)
    )


def log_api_call(provider: str, model: str, tokens: dict):
    """Log API call details"""
    logger.debug(
        f"API call to {provider}",
        model=model,
        input_tokens=tokens.get("input", 0),
        output_tokens=tokens.get("output", 0)
    )


def log_rate_limit(provider: str, wait_time: float):
    """Log rate limiting events"""
    logger.warning(
        f"Rate limited by {provider}",
        wait_time=f"{wait_time:.2f}s"
    )


# Export main logger
__all__ = [
    'logger',
    'setup_logging',
    'console',
    'create_progress_bar',
    'BenchmarkLogger',
    'log_model_info',
    'log_api_call',
    'log_rate_limit'
]