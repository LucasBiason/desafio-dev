"""Logging configuration helpers."""

import logging


class LoggerConfig:
    """Handles root logger setup and per-module logger creation."""

    DEFAULT_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

    @classmethod
    def configure_root_logger(cls, level: str = "INFO", log_file: str | None = None) -> None:
        """Configures the root logger with a console handler and optional file handler."""
        root = logging.getLogger()
        root.setLevel(getattr(logging, level.upper(), logging.INFO))

        formatter = logging.Formatter(cls.DEFAULT_FORMAT)

        if not root.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root.addHandler(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)

    @classmethod
    def get_logger(cls, name: str, level: str | None = None) -> logging.Logger:
        """Returns a logger for the given module name, optionally overriding its level."""
        logger = logging.getLogger(name)
        if level:
            logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        return logger


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """Shortcut for LoggerConfig.get_logger()."""
    return LoggerConfig.get_logger(name, level)


def configure_logging(level: str = "INFO", log_file: str | None = None) -> None:
    """Shortcut for LoggerConfig.configure_root_logger()."""
    LoggerConfig.configure_root_logger(level, log_file)
