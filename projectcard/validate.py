import os
from pathlib import Path
from typing import Union

import json
from json import JSONDecodeError

from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError
import jsonref

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


def _load_schema(schema_absolute_path):

    base_path = os.path.dirname(schema_absolute_path)
    base_uri = "file://{}/".format(base_path)

    with open(schema_absolute_path) as schema_file:
        _s = jsonref.replace_refs(
            _open_json(schema_absolute_path),
            base_uri=base_uri,
            proxies=False,
            lazy_load=False,
        )
        CardLogger.debug(f"----\n{schema_absolute_path}\n{_s}")
        return _s


def package_schema(
    schema_path: Union[Path, str] = PROJECTCARD_SCHEMA,
    outfile_path: Union[Path, str] = None,
) -> None:
    """Consolidates referenced schemas into a single schema and writes it out.

    Args:
        schema_path: Schema to read int and package. Defaults to PROJECTCARD_SCHEMA.
        outfile: Where to write out packaged schema. Defaults to schema_path.basepath.packaged.json
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


def validate_schema_file(schema_path=PROJECTCARD_SCHEMA):
    try:
        _schema_data = _load_schema(schema_path)
        # _resolver = _ref_resolver(schema_path,_schema_data)
        validate({}, schema=_schema_data)  # ,resolver=_resolver)
    except ValidationError as e:
        pass
    except SchemaError as e:
        CardLogger.error(e)
        raise SchemaError(f"{e}")


def validate_card(jsondata, schema_path=PROJECTCARD_SCHEMA):
    """Validates json-like data to specified schema.

    Args:
        jsondata: json-like data to validate.
        schema: schema to validate to, in json-schema format. Defaults to PROJECTCARD_SCHEMA.

    Raises:
        ValidationError: _description_
        SchemaError: _description_
    """

    CardLogger.debug(f"Validating: {jsondata['project']}")
    try:
        _schema_data = _load_schema(schema_path)
        validate(jsondata, schema=_schema_data)
    except ValidationError as e:
        CardLogger.error(e)
        raise ValidationError(f"{e}")
    except SchemaError as e:
        CardLogger.error(e)
        raise SchemaError(f"{e}")
    return True
