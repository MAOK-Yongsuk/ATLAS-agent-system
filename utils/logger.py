import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
import json
from typing import Dict, Any

class CustomFormatter(logging.Formatter):
    """Custom formatter with colors and structured output"""
    
    # ANSI escape sequences for colors
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'      # Reset color
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Add timestamp in ISO format
        record.timestamp = datetime.now().isoformat()
        
        # Color the log level
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.colored_levelname = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        # Add custom formatting for extra fields
        extra_data = {}
        for key, value in vars(record).items():
            if key not in logging.LogRecord.__dict__ and key not in ['timestamp', 'colored_levelname']:
                extra_data[key] = value
        
        # Format the message
        base_message = f"[{record.timestamp}] {record.colored_levelname}: {record.getMessage()}"
        
        # Add extra data if present
        if extra_data:
            try:
                extra_str = json.dumps(extra_data, indent=2)
                base_message += f"\nExtra Data: {extra_str}"
            except:
                pass
        
        # Add traceback for errors
        if record.exc_info:
            base_message += f"\n{self.formatException(record.exc_info)}"
            
        return base_message

def setup_logger(name: str) -> logging.Logger:
    """Set up and configure logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    
    # File Handler (with rotation)
    file_handler = RotatingFileHandler(
        filename=log_dir / "study_assistant.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(
        logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    )
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = __name__) -> logging.Logger:
    """Get or create a logger instance"""
    return setup_logger(name)

class LoggerMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
    
    def log_method_call(self, method_name: str, **kwargs):
        """Log method calls with parameters"""
        self.logger.debug(
            f"Calling {method_name}",
            extra={
                'parameters': kwargs,
                'class': self.__class__.__name__
            }
        )