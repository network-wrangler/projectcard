import json
import os
from json import JSONDecodeError
from pathlib import Path
from typing import Union

import jsonref
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError

from .logger import CardLogger

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTCARD_SCHEMA = os.path.join(ROOTDIR, "schema", "projectcard.json")


def _open_json(schema_path: str) -> dict:
    try:
        with open(schema_path, "r") as file:
            return json.loads(file.read())
    except FileNotFoundError:
        CardLogger.error(f"Schema not found: {schema_path}")
        raise Exception("Schema definition missing")
    except JSONDecodeError:
        CardLogger.error(f"Schema not valid JSON: {schema_path}")
        raise Exception("Schema definition invalid")


def _load_schema(schema_absolute_path: Union[Path, str]) -> dict:
    base_path = os.path.dirname(schema_absolute_path)
    base_uri = "file://{}/".format(base_path)

    _s = jsonref.replace_refs(
        _open_json(schema_absolute_path),
        base_uri=base_uri,
        proxies=False,
        lazy_load=False,
    )
    # CardLogger.debug(f"----\n{schema_absolute_path}\n{_s}")
    return _s


def package_schema(
    schema_path: Union[Path, str] = PROJECTCARD_SCHEMA,
    outfile_path: Union[Path, str] = None,
) -> None:
    """Consolidates referenced schemas into a single schema and writes it out.

    Args:
        schema_path: Schema to read int and package. Defaults to PROJECTCARD_SCHEMA which is
            os.path.join(ROOTDIR, "schema", "projectcard.json").
        outfile_path: Where to write out packaged schema. Defaults
            to schema_path.basepath.packaged.json
    """
    schema_path = Path(schema_path)
    _s_data = _load_schema(schema_path)
    if outfile_path is None:
        outfile_path = (
            schema_path.parent / f"{schema_path.stem}packaged.{schema_path.suffix}"
        )
    outfile_path = Path(outfile_path)
    with open(outfile_path, "w") as outfile:
        json.dump(_s_data, outfile, indent=4)
    CardLogger.info(f"Wrote {schema_path.stem} to {outfile_path.stem}")


def validate_schema_file(schema_path: Union[Path, str] = PROJECTCARD_SCHEMA) -> bool:
    """Validates that a schema file is a valid JSON-schema.

    Args:
        schema_path: _description_. Defaults to PROJECTCARD_SCHEMA which is
             os.path.join(ROOTDIR, "schema", "projectcard.json").
    """
    try:
        _schema_data = _load_schema(schema_path)
        # _resolver = _ref_resolver(schema_path,_schema_data)
        validate({}, schema=_schema_data)  # ,resolver=_resolver)
    except ValidationError:
        pass
    except SchemaError as e:
        CardLogger.error(e)
        raise SchemaError(f"{e}")
    return True


def validate_card(
    jsondata: dict, schema_path: Union[str, Path] = PROJECTCARD_SCHEMA
) -> bool:
    """Validates json-like data to specified schema.

    Args:
        jsondata: json-like data to validate.
        schema_path: path to schema to validate to.
            Defaults to PROJECTCARD_SCHEMA which is
            os.path.join(ROOTDIR, "schema", "projectcard.json")

    Raises:
        ValidationError: If jsondata doesn't conform to specified schema.
        SchemaError: If schema itself is not valid.
    """

    CardLogger.debug(f"Validating: {jsondata['project']}")
    try:
        _schema_data = _load_schema(schema_path)
        validate(jsondata, schema=_schema_data)
    except ValidationError as e:
        CardLogger.error(f"---- Error validating {jsondata['project']} ----")
        CardLogger.error(e)
        raise ValidationError(f"{e}")
    except SchemaError as e:
        CardLogger.error(e)
        raise SchemaError(f"{e}")
    return True
