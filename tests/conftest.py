from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def base_dir():
    return Path(__file__).resolve().parent.parent / "projectcard"


@pytest.fixture(scope="session")
def test_dir():
    return Path(__file__).resolve().parent


@pytest.fixture(scope="session")
def test_out_dir(test_dir: Path):
    _test_out_dir = test_dir / "out"
    if not _test_out_dir.exists():
        _test_out_dir.mkdir()
    return _test_out_dir


@pytest.fixture(scope="session", autouse=True)
def _test_logging(test_out_dir: Path) -> None:
    from projectcard import setup_logging

    setup_logging(
        info_log_filename=test_out_dir / "tests.info.log",
        debug_log_filename=test_out_dir / "tests.debug.log",
    )


@pytest.fixture(scope="session")
def schema_dir(base_dir: Path):
    return base_dir / "schema"


@pytest.fixture(scope="session")
def all_schema_files(schema_dir):
    schema_files = [p for p in schema_dir.glob("**/*.json")]
    return schema_files


@pytest.fixture(scope="session")
def example_dir(base_dir: Path):
    return base_dir / "examples"


@pytest.fixture(scope="session")
def all_example_cards(example_dir):
    """Card files should pass."""
    card_files = list(example_dir.iterdir())
    return card_files
