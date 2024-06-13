from pathlib import Path

import pytest

from projectcard.update import update_schema_for_card_file


@pytest.fixture(scope="session")
def all_v0_card_files(test_dir):
    """Card files which should fail."""
    _card_dir = Path(test_dir) / "data" / "cards"
    v0_card_files = list(Path(_card_dir).rglob("*[vV]0.*[yY]*[mM][lL]"))
    if not v0_card_files:
        raise ValueError(f"No v0 card files found in {_card_dir}")
    return v0_card_files


def test_convert_to_v0_cards(all_v0_card_files, test_out_dir):
    output_path = test_out_dir
    for p in all_v0_card_files:
        update_schema_for_card_file(p, output_path)
