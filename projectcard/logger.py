"""Logging module for the projectcard package."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

CardLogger = logging.getLogger("CardLogger")


def setup_logging(
    info_log_filename: Optional[Path] = None,
    debug_log_filename: Optional[Path] = None,
    log_to_console: bool = False,
):
    """Sets up the CardLogger w.r.t. the debug file location and if logging to console.

    Args:
        info_log_filename: the location of the log file that will get created to add the INFO log.
            The INFO Log is terse, just gives the bare minimum of details.
            Defaults to file in cwd() `cards_[datetime].log`. To turn off logging to a file,
            use log_filename = None.
        debug_log_filename: the location of the log file that will get created to add the
            DEBUG log. The DEBUG log is very noisy, for debugging. Defaults to file in cwd()
            `cards_[datetime].log`. To turn off logging to a file, use log_filename = None.
        log_to_console: if True, logging will go to the console at DEBUG level. Defaults to False.
    """
    # add function variable so that we know if logging has been called
    setup_logging.called = True

    # Clear handles if any exist already
    CardLogger.handlers = []

    CardLogger.setLevel(logging.DEBUG)

    FORMAT = logging.Formatter(
        "%(asctime)-15s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S,"
    )
    default_log_filename = f"cards_{datetime.now().strftime('%Y_%m_%d__%H_%M_%S')}.info.log"
    info_log_filename = info_log_filename or Path.cwd() / default_log_filename

    info_file_handler = logging.FileHandler(Path(info_log_filename))
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(FORMAT)
    CardLogger.addHandler(info_file_handler)

    # create debug file only when debug_log_filename is provided
    if debug_log_filename:
        debug_log_handler = logging.FileHandler(Path(debug_log_filename))
        debug_log_handler.setLevel(logging.DEBUG)
        debug_log_handler.setFormatter(FORMAT)
        CardLogger.addHandler(debug_log_handler)

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(FORMAT)
        CardLogger.addHandler(console_handler)
