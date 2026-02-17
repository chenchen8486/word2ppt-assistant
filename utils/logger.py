import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Define log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class GuiHandler(logging.Handler):
    """
    A custom logging handler that sends logs to a GUI callback function.
    """
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        if self.callback:
            try:
                msg = self.format(record)
                self.callback(msg)
            except Exception:
                self.handleError(record)

def setup_logger(name="Exam2PPT", log_file="logs/app.log", level=logging.INFO, gui_callback=None):
    """
    Sets up the logger with file and console handlers.
    
    Args:
        name (str): The name of the logger.
        log_file (str): The path to the log file.
        level (int): The logging level.
        gui_callback (callable): A function to call with log messages (for GUI display).
        
    Returns:
        logging.Logger: The configured logger instance.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # File Handler
    # Ensure log directory exists if log_file contains a path
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # GUI Handler (Optional)
    if gui_callback:
        gui_handler = GuiHandler(gui_callback)
        gui_handler.setFormatter(formatter)
        gui_handler.setLevel(level)
        logger.addHandler(gui_handler)

    logger.info("Logger initialized.")
    return logger

def get_logger(name="Exam2PPT"):
    """
    Returns the existing logger.
    """
    return logging.getLogger(name)
