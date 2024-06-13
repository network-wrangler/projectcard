import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def update_datamodels():
    """Run update_data_models script before every test run."""
    base_dir = Path(__file__).resolve().parent.parent
    update_script = base_dir / "bin" / "update_data_models"
    subprocess.run([update_script], check=True)


@pytest.fixture(scope="session")
def base_dir():
    return Path(__file__).resolve().parent.parent


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
def test_logging(test_out_dir: Path):
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
    schema_files = [p for p in Path(schema_dir).glob("**/*.json")]
    return schema_files


@pytest.fixture(scope="session")
def example_dir(base_dir: Path):
    return Path(base_dir) / "examples"


@pytest.fixture(scope="session")
def all_example_cards(example_dir):
    """Card files should pass."""
    card_files = list(example_dir.iterdir())
    return card_files
