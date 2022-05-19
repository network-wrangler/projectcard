"""Testing of basic examples.

USAGE:
    pytest --log-cli-level=10
"""
import logging
import os

from projectcard.projectcard import read as read_projectcard
from projectcard.projectcard import validate

logger = logging.getLogger(__name__)

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLEDIR = os.path.join(ROOTDIR, "examples")


def test_read_dir():
    cards = read_projectcard(EXAMPLEDIR)
    print(f"Cards: {cards}")
    logger.debug(f"Cards: {cards}")
