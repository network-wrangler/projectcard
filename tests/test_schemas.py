"""Testing of schemas.

USAGE:
    pytest tests/test_schemas.py
"""

import os
from pathlib import Path

import pytest
from jsonschema import validate

from projectcard import CardLogger, validate_schema_file
from projectcard.validate import _load_schema, _open_json, package_schema


def test_schemas_valid_json(all_schema_files):
    for s in all_schema_files:
        _open_json(s)
    CardLogger.info(f"Evaluated json valid for {len(all_schema_files)} schema files")


def test_projectcard_package(test_out_dir):
    _outfile_path = os.path.join(test_out_dir, "projectcard.testpackage.json")
    package_schema(outfile_path=_outfile_path)
    validate_schema_file(_outfile_path)


def test_individual_schemas(all_schema_files):
    for s in all_schema_files:
        validate_schema_file(s)
    CardLogger.info(f"Evaluated schema valid for {len(all_schema_files)} schema files")


@pytest.fixture(scope="session")
def all_bad_schema_files(test_dir):
    """Schema files which should fail."""
    schemas_dir = Path(test_dir) / "data" / "schemas"
    bad_schema_files = [p for p in schemas_dir.glob("**/*bad.json")]
    return bad_schema_files


def test_bad_schema(all_bad_schema_files):
    for s in all_bad_schema_files:
        try:
            validate_schema_file(s)
        except:
            pass
        else:
            CardLogger.error(f"Schema should not be valid: {s}")
            raise ValueError(
                "Schema shouldn't be valid but is not raising an error in validate_schema_file"
            )
    CardLogger.info(f"Evaluated {len(all_bad_schema_files)} bad schema files")


def test_json_schema_examples_valid(all_schema_files):
    """If referenced json schema has examples listed, test that they are valid."""
    for s in all_schema_files:
        CardLogger.info(f"Validating Examples for {s}")
        schema = _load_schema(s)
        if "examples" in schema:
            for example in schema["examples"]:
                validate(example, schema=schema)
    CardLogger.info(f"Evaluated examples valid for {len(all_schema_files)} schema files")
