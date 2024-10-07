"""Testing of basic examples.

USAGE:
    pytest --log-cli-level=10
"""

from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError

from projectcard import CardLogger, read_card, read_cards


def test_read_single_card(example_dir):
    CardLogger.info("Testing that a single card in example directory can be read in.")
    _ex_name = "example roadway add"
    _ex_file = "roadway-add.yml"
    _card_path = example_dir / _ex_file
    CardLogger.debug(f"Reading {_card_path}")
    card = read_card(_card_path)
    CardLogger.debug(f"Read card:\n {card}")
    assert card.project == _ex_name


def test_example_valid(all_example_cards):
    CardLogger.info("Testing that all cards in example directory are valid.")
    errors = []
    ok = []
    for pc_path in all_example_cards:
        try:
            read_card(pc_path, validate=True)
        except ValidationError as e:
            errors.append(str(pc_path))
            CardLogger.error(e)
        else:
            ok.append(str(pc_path))
    _delim = "\n - "
    CardLogger.debug(f"Valid Cards: {_delim}{_delim.join(ok)}")
    if errors:
        msg = f"Errors in {len(errors)} of {len(all_example_cards)} example project cards."
        CardLogger.error(f"Card Validation Errors: {_delim}{_delim.join(errors)}")
        raise ValidationError(msg)

    CardLogger.info(f"Evaluated {len(all_example_cards)} schema files")


def test_bad_cards(test_dir):
    card_dir = Path(test_dir) / "data" / "cards"
    bad_card_files = [p for p in card_dir.glob("**/*bad.yaml")]
    non_failing_cards = []
    for s in bad_card_files:
        try:
            read_card(s, validate=True)
        except ValidationError:
            pass
        else:
            non_failing_cards.append(s)
    if non_failing_cards:
        msg = f"Failed to catch errors for: {non_failing_cards}"
        CardLogger.error(msg)
        raise AssertionError(msg)
    CardLogger.info(f"Evaluated {len(bad_card_files)} bad card files")
