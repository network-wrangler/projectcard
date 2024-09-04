"""Testing of basic examples.

USAGE:
    pytest --log-cli-level=10
"""

import os
from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError

from projectcard import CardLogger, read_card, read_cards


def test_read_single_card(example_dir):
    CardLogger.info("Testing that a single card in example directory can be read in.")
    _ex_name = "example roadway add"
    _ex_file = "roadway-add.yml"
    _card_path = os.path.join(example_dir, _ex_file)
    CardLogger.debug(f"Reading {_card_path}")
    card = read_card(_card_path)
    CardLogger.debug(f"Read card:\n {card}")
    assert card.project == _ex_name


def test_example_valid(all_example_cards):
    CardLogger.info("Testing that all cards in example directory are valid.")
    errors = []
    ok = []
    for pc_path in all_example_cards:
        card = read_card(pc_path)
        CardLogger.debug(f"Evaluating: {str(pc_path)}")
        try:
            assert card.valid
        except ValidationError as e:
            errors.append(str(pc_path))
            CardLogger.error(e)
        except AssertionError as e:
            errors.append(str(pc_path))
            CardLogger.error(e)
        else:
            ok.append(str(pc_path))
    _delim = "\n - "
    CardLogger.debug(f"Valid Cards: {_delim}{_delim.join(ok)}")
    if errors:
        CardLogger.error(f"Card Validation Errors: {_delim}{_delim.join(errors)}")
        raise ValidationError(
            f"Errors in {len(errors)} of {len(all_example_cards)} example project cards"
        )

    CardLogger.info(f"Evaluated {len(all_example_cards)} schema files")


@pytest.fixture(scope="session")
def all_bad_card_files(test_dir):
    """Card files which should fail."""
    _card_dir = Path(test_dir) / "data" / "cards"
    bad_card_files = [p for p in _card_dir.glob("**/*bad.yaml")]
    return bad_card_files


def test_bad_cards(all_bad_card_files):
    for s in all_bad_card_files:
        try:
            cards = read_cards(s)
            assert all([c.valid for c in cards.values()])
        except:
            pass
        else:
            CardLogger.error(f"Card should not be valid: {s}")
            raise ValueError(
                "Card shouldn't be valid but is not raising an error in validate_schema_file"
            )
    CardLogger.info(f"Evaluated {len(all_bad_card_files)} bad card files")
