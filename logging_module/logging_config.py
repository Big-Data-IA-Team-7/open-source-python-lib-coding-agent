import logging
from logging.handlers import RotatingFileHandler
import os
from functools import wraps
from time import time

def setup_logging(log_dir="logs"):
    """Configure application-wide logging with all levels"""
    os.makedirs(log_dir, exist_ok=True)
    
    # Create formatter for all handlers
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s'
    )
    
    # Setup handlers for different levels
    debug_handler = RotatingFileHandler(
        f"{log_dir}/debug.log", 
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    debug_handler.setFormatter(file_formatter)
    debug_handler.setLevel(logging.DEBUG)
    
    info_handler = RotatingFileHandler(
        f"{log_dir}/info.log", 
        maxBytes=10485760,
        backupCount=5
    )
    info_handler.setFormatter(file_formatter)
    info_handler.setLevel(logging.INFO)
    
    warning_handler = RotatingFileHandler(
        f"{log_dir}/warning.log", 
        maxBytes=10485760,
        backupCount=5
    )
    warning_handler.setFormatter(file_formatter)
    warning_handler.setLevel(logging.WARNING)
    
    error_handler = RotatingFileHandler(
        f"{log_dir}/error.log", 
        maxBytes=10485760,
        backupCount=5
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    
    critical_handler = RotatingFileHandler(
        f"{log_dir}/critical.log", 
        maxBytes=10485760,
        backupCount=5
    )
    critical_handler.setFormatter(file_formatter)
    critical_handler.setLevel(logging.CRITICAL)
    
    # Setup console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)  # Console shows INFO and above
    
    # Setup root logger at DEBUG level to catch all
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything, handlers will filter
    
    # Add all handlers
    handlers = [
        debug_handler,
        info_handler,
        warning_handler,
        error_handler,
        critical_handler,
        console_handler
    ]
    
    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    for handler in handlers:
        root_logger.addHandler(handler)
    
    for lib in ['snowflake', 'botocore', 'boto3', 'langsmith', 'langchain', 'httpcore', 'openai', 'pinecone']:
        logging.getLogger(lib).setLevel(logging.CRITICAL)
    
    return root_logger

def get_logger(name):
    """Get a logger for a specific module"""
    return logging.getLogger(name)

def log_execution_time(logger):
    """Decorator to log function execution time"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time()
            try:
                result = func(*args, **kwargs)
                duration = time() - start
                logger.debug(f"{func.__name__} took {duration:.2f} seconds to execute")
                return result
            except Exception as e:
                duration = time() - start
                logger.error(
                    f"{func.__name__} failed after {duration:.2f} seconds. Error: {str(e)}", 
                    exc_info=True
                )
                raise
        return wrapper
    return decorator