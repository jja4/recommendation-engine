"""
Logging configuration for the Humanoo Wellness Assistant.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(
    log_dir: str = "logs",
    log_level: int = logging.INFO,
    include_console: bool = True
) -> logging.Logger:
    """
    Configure logging to both file and console.
    
    Args:
        log_dir: Directory to save log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        include_console: Whether to also log to console
        
    Returns:
        Configured logger instance
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create timestamp for log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"humanoo_{timestamp}.log"
    
    # Create logger
    logger = logging.getLogger("humanoo")
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # File handler - detailed format
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Console handler - simpler format
    if include_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_format = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized. Log file: {log_file}")
    
    return logger


def get_logger() -> logging.Logger:
    """Get the humanoo logger instance."""
    return logging.getLogger("humanoo")
