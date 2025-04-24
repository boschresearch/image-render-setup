"""Utitlity functions for logging."""

import enum
import sys
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from . import util


class ELogLevel(str, enum.Enum):
    """Log levels."""

    NONE = "NONE"
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ELogFormat(enum.Enum):
    """Logging format enum."""

    DEFAULT = 0
    SIMPLE = 1


@dataclass
class LogConfig:
    """Log configuration dataclass.

    stdout_level (int): The verbose level.
    stdout_format (ELogFormat): The format of the log.
    stderr_level (int): Log to stderr. 0: disable, 1: ERROR, 2: WARNING, 3: INFO, 4: DEBUG, 5: TRACE.
    file_level (int): Log to file in '~/.xtar/logs'. 0: disable, 1: ERROR, 2: WARNING, 3: INFO, 4: DEBUG, 5: TRACE.
    file_ret_days (int): How many days to keep the logfile. Defaults to 7.
    file_type_json (bool): Whether to log as JSON with many more details. Defaults to False.
    name (str, optional): The name of the log file.
                                This is not the full log file name but part of it. Defaults to "".
    """

    stdout_level: int = -1
    stdout_format: ELogFormat = ELogFormat.DEFAULT
    stderr_level: int = -1
    file_level: int = -1
    file_ret_days: int = 7
    file_type_json: bool = False
    name: str = ""
    _enabled: bool = False

    def __post_init__(self) -> None:
        """Post init."""
        self._enabled = self.stdout_level > 0 or self.stderr_level > 0 or self.file_level > 0

    @property
    def enabled(self) -> bool:
        """Check if logging is enabled."""
        return self._enabled

    @property
    def stdout_log(self) -> ELogLevel:
        """Get the stdout log level."""
        return debug_to_log_level(self.stdout_level)

    @property
    def stderr_log(self) -> ELogLevel:
        """Get the stderr log level."""
        return debug_to_log_level(self.stderr_level)

    @property
    def file_log(self) -> ELogLevel:
        """Get the file log level."""
        return debug_to_log_level(self.file_level)


def debug_to_log_level(level: int) -> ELogLevel:
    """Set the debug level.

    Args:
        level (int): The debug level. 0: disable, 1: ERROR, 2: WARNING, 3: INFO, 4: DEBUG, 5: TRACE.
    """
    if level <= 0:
        return ELogLevel.NONE

    if level == 1:
        return ELogLevel.ERROR

    if level == 2:
        return ELogLevel.WARNING

    if level == 3:
        return ELogLevel.INFO

    if level == 4:
        return ELogLevel.DEBUG

    return ELogLevel.TRACE


def enable() -> None:
    """Enable the logger."""
    logger.enable("xtar")


def disable() -> None:
    """Disable the logger."""
    logger.disable("xtar")


def to_stdout(level: ELogLevel = ELogLevel.INFO, format_type: ELogFormat = ELogFormat.DEFAULT) -> None:
    """Log to stdout with the specified log level.

    Args:
        level: The log level to log at.
        format_type: The log format type.
    """
    if level == ELogLevel.NONE:
        return

    if format_type == ELogFormat.DEFAULT:
        logger.add(
            sink=sys.stdout,
            level=level.value,
            # format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        )
    elif format_type == ELogFormat.SIMPLE:
        logger.level("INFO", color="<green>", icon="✔")
        logger.level("SUCCESS", color="<green><bold>", icon="✔")
        logger.add(
            sink=sys.stdout,
            level=level.value,
            format="<level>{message}</level>",
        )
    else:
        raise ValueError(f"Unknown format type: {format_type}")


def to_stderr(level: ELogLevel = ELogLevel.ERROR) -> None:
    """Log to stderr with the specified log level.

    Args:
        level: The log level to log at.
    """
    if level == ELogLevel.NONE:
        return

    logger.add(
        sink=sys.stderr,
        level=level.value,
        # format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )


def to_file(level: ELogLevel = ELogLevel.ERROR, retention_days: int = 7, as_json: bool = False, name: str = "") -> None:
    """Log to file.

    Args:
        level (ELogLevel, optional): Logging level. Defaults to ELogLevel.ERROR.
        retention_days (int, optional): How many days to keep the logfile. Defaults to 7.
        as_json (bool, optional): Whether to log as JSON with many more details. Defaults to False.
        name (str, optional): The name of the log file. Defaults to "".
    """
    if level == ELogLevel.NONE:
        return

    log_path: Path = util.NormPath("~/.catharsys/logs")
    log_path.mkdir(parents=True, exist_ok=True)
    filename: str = f"xtar_{name}_{{time}}.log" if len(name) > 0 else "xtar_{time}.log"
    log_file: Path = log_path / filename

    logger.add(
        sink=log_file.as_posix(),
        level=level.value,
        # format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        retention=f"{retention_days} days",
        serialize=as_json,
    )


_log_config: LogConfig = LogConfig()


def set_logging(config: LogConfig) -> None:
    """Set the logging.

    Args:
        config (LogConfig): The log configuration.
    """
    global _log_config  # noqa: PLW0603
    _log_config = config

    if not _log_config.enabled:
        disable()
        return

    enable()

    to_stdout(config.stdout_log)
    to_stderr(config.stderr_log)
    to_file(config.file_log, config.file_ret_days, config.file_type_json, config.name)


def get_logging() -> LogConfig:
    """Get the logging settings."""
    return _log_config


# Remove the default logger
logger.remove(0)
# Disable the xtar logger for all logs from the xtar lib.
# Can be enabled by a script using this lib by calling 'enable()'.
disable()
