import os
from pathlib import Path

import pytest

from projectcard import CardLogger


@pytest.fixture(scope="session")
def base_dir():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


@pytest.fixture(scope="session")
def test_dir():
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(scope="session")
def test_out_dir(test_dir):
    _test_out_dir = os.path.join(test_dir, "out")
    if not os.path.exists(_test_out_dir):
        os.mkdir(_test_out_dir)
    return _test_out_dir


@pytest.fixture(scope="session", autouse=True)
def test_logging(test_out_dir):
    from projectcard import setup_logging

    setup_logging(
        info_log_filename=os.path.join(test_out_dir, "tests.info.log"),
        debug_log_filename=os.path.join(test_out_dir, "tests.debug.log"),
    )


@pytest.fixture(scope="session")
def schema_dir(base_dir):
    return os.path.join(base_dir, "schema")


@pytest.fixture(scope="session")
def all_schema_files(schema_dir):
    schema_files = [p for p in Path(schema_dir).glob("**/*.json")]
    return schema_files


@pytest.fixture(scope="session")
def all_bad_schema_files(test_dir):
    """Schema files which should fail"""
    bad_schema_files = [
        p for p in Path(test_dir + "data" + "schemas").glob("**/*bad.json")
    ]
    return bad_schema_files


@pytest.fixture(scope="session")
def example_dir(base_dir):
    return Path(base_dir) /  "examples"

@pytest.fixture(scope="session")
def all_example_cards(example_dir):
    """Card files should pass"""
    card_files =  list(example_dir.iterdir())
    return card_files


@pytest.fixture(scope="session")
def all_bad_card_files(test_dir):
    """Card files which should fail"""
    bad_card_files = [p for p in Path(test_dir + "data" + "cards").glob("**/*bad.yaml")]
    return bad_card_files
