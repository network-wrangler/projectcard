"""Testing of basic examples.

USAGE:
    pytest --log-cli-level=10
"""
import pytest
from jsonschema.exceptions import ValidationError

from projectcard import CardLogger, read_cards


def test_read_dir(all_example_cards, example_dir):
    CardLogger.info("Testing that all cards in example directory can be read in.")
    _cards = all_example_cards
    delim = "\n--------\n"
    CardLogger.debug(f"Cards:{delim}{delim.join(str(v) for v in _cards.values())}")
    from projectcard.io import _get_cardpath_list

    _expected_cards = _get_cardpath_list(example_dir)
    assert len(_cards) == len(_expected_cards)


@pytest.mark.menow
def test_example_valid(all_example_cards):
    CardLogger.info("Testing that all cards in example directory are valid.")
    errors = []
    ok = []
    for project, card in all_example_cards.items():
        CardLogger.debug(f"Evaluating: {project}")
        try:
            assert card.valid
        except ValidationError as e:
            errors.append(project)
            CardLogger.error(e)
        except AssertionError as e:
            errors.append(project)
            CardLogger.error(e)
        else:
            ok.append(project)
    _delim = "\n - "
    CardLogger.debug(f"Valid Cards: {_delim}{_delim.join(ok)}")
    if errors:
        CardLogger.error(f"Card Validation Errors: {_delim}{_delim.join(errors)}")
        raise ValidationError(
            f"Errors in {len(errors)} of {len(all_example_cards)} example project cards"
        )

    CardLogger.info(f"Evaluated {len(all_example_cards)} schema files")


def test_bad_cards(all_bad_card_files):
    for s in all_bad_card_files:
        try:
            cards = read_cards(s)
            assert all([c.valid for c in cards.values()])
        except:
            pass
        else:
            CardLogger.error(f"Schema should not be valid: {s}")
            raise ValueError(
                "Schema shouldn't be valid but is not raising an error in validate_schema_file"
            )
    CardLogger.info(f"Evaluated {len(all_bad_card_files)} bad card files")
