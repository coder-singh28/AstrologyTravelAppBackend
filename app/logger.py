"""
Logger Configuration Module
Sets up application logging with both console and file handlers.
- Console output with UTF-8 encoding for Windows compatibility
- Rotating file handler to manage log file sizes
- Standard format: timestamp | level | name | message
"""

import logging
from logging.handlers import RotatingFileHandler
import sys
from datetime import datetime


def setup_logger():
    """
    Configure and return application logger with console and file handlers.
    
    Configuration:
    - Logger Name: "AstrologyTravelAppBackend"
    - Level: INFO and above
    - Console: UTF-8 encoded stdout with formatter
    - File: Daily rotating logs (5MB per file, 5 backups)
    - Format: "YYYY-MM-DD HH:MM:SS | LEVEL | NAME | MESSAGE"
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger("AstrologyTravelAppBackend")
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers on multiple calls
    if logger.handlers:
        return logger
    
    # Console handler with UTF-8 encoding (for Windows compatibility)
    console_handler = logging.StreamHandler(sys.stdout)
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    console_handler.setLevel(logging.INFO)
    
    # File handler with rotation
    log_date = datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/app_{log_date}.log"
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB per file
        backupCount=5  # Keep 5 backup files
    )
    file_handler.setLevel(logging.INFO)
    
    # Standard log format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
