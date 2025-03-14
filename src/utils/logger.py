import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

class Logger:
    _instance: Optional['Logger'] = None
    
    def __init__(self, log_dir: str = 'logs'):
        """Initialize the logger.
        
        Args:
            log_dir: Directory to store log files
        """
        if Logger._instance is not None:
            raise RuntimeError("Logger is a singleton - use get_logger() instead")
        
        self.log_dir = log_dir
        self._setup_logger()
        Logger._instance = self
    
    @classmethod
    def get_logger(cls, log_dir: str = 'logs') -> logging.Logger:
        """Get or create the logger instance.
        
        Args:
            log_dir: Directory to store log files
            
        Returns:
            logging.Logger: Configured logger instance
        """
        if cls._instance is None:
            cls(log_dir)
        return logging.getLogger('website_tracker')
    
    def _setup_logger(self) -> None:
        """Set up logging configuration."""
        logger = logging.getLogger('website_tracker')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_path = Path(self.log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # File handler for all logs
        log_file = log_path / f"tracker_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # Error file handler
        error_file = log_path / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatters and add them to the handlers
        detailed_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )
        
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)
    
    @staticmethod
    def log_exception(e: Exception, context: str = '') -> None:
        """Log an exception with context.
        
        Args:
            e: Exception to log
            context: Additional context about where/why the error occurred
        """
        logger = logging.getLogger('website_tracker')
        if context:
            logger.error(f"{context}: {str(e)}", exc_info=True)
        else:
            logger.error(str(e), exc_info=True)