"""
Logger configuration untuk aplikasi.
Menggunakan Python logging dengan format yang terstruktur.
"""

import logging
import sys
from typing import Optional

from app.core.config import settings


def setup_logger(
    name: str = "app",
    level: Optional[int] = None,
) -> logging.Logger:
    """
    Setup logger dengan konfigurasi standar.
    
    Args:
        name: Nama logger
        level: Level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger yang sudah dikonfigurasi
    """
    logger = logging.getLogger(name)
    
    # Set level berdasarkan debug mode jika tidak dispesifikasikan
    if level is None:
        level = logging.DEBUG if settings.debug else logging.INFO
    
    logger.setLevel(level)
    
    # Hindari duplikasi handler
    if logger.handlers:
        return logger
    
    # Format log
    if settings.debug:
        # Format detail untuk development
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # Format simple untuk production
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Logger default untuk aplikasi
logger = setup_logger()
