import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os


def setup_logger(
        name="global_logger",
        log_dir="logs",
        to_console=True,
        level=logging.ERROR,
        backup_count=7
) -> logging.Logger:
    """
    创建一个按天分割的 logger 实例，并返回
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

    # 避免重复添加 handler（如 setup_logger 被多次调用）
    if logger.handlers:
        return logger

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")

    file_handler = TimedRotatingFileHandler(
        log_path,
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding='utf-8',
        utc=False
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.propagate = False
    return logger
