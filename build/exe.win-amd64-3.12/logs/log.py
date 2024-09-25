import logging
import os
from typing import Literal

from config import config


class Logger:
    """
    A class to handle logging with different log types.

    Attributes:
    LOG_DIR (str): The directory where log files will be stored.
    GENERAL_LOG_FILE (str): Base filename for general log files.
    RETURN_LOG_FILE (str): Base filename for return log files.
    LOG_FILE_EXTENSION (str): The extension for log files.
    """

    def __init__(self, log_type: Literal["general", "return"] = "general"):
        """
        Initialize the Logger with a specific log type.

        Parameters:
        log_type (str): The type of the log, either 'general' or 'return'.
        """
        self.log_type = log_type
        self.LOG_DIR = os.path.abspath(config["log"]["dir"])
        self.LOG_FILE_EXTENSION = config["log"]["log_file_extension"]
        self.GENERAL_LOG_FILE = config["log"]["general_log_file"]
        self.RETURN_LOG_FILE = config["log"]["return_log_file"]
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger with specified log type.

        Returns:
        logging.Logger: Configured logger instance.
        """
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)
        log_filename = (
            self.GENERAL_LOG_FILE
            if self.log_type == "general"
            else self.RETURN_LOG_FILE
        )
        log_file_path = os.path.join(self.LOG_DIR, log_filename)
        logger = logging.getLogger(self.log_type)

        if not logger.hasHandlers():
            logger.setLevel(logging.INFO)
            file_handler = logging.FileHandler(
                self._get_segmented_log_filename(log_file_path), encoding="utf-8"
            )
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )
            logger.addHandler(file_handler)
            logger.propagate = False

        return logger

    def _get_segmented_log_filename(self, base_filename: str) -> str:
        """
        Generate a segmented log filename based on existing log file size.

        Parameters:
        base_filename (str): The base filename for the log.

        Returns:
        str: The filename for the next log segment.
        """
        segment = 0
        while os.path.exists(f"{base_filename}_{segment:02d}{self.LOG_FILE_EXTENSION}"):
            segment += 1

        return f"{base_filename}_{segment:02d}{self.LOG_FILE_EXTENSION}"
