"""Validates ProjectCard JSON data against a JSON schema."""

import json
from json import JSONDecodeError
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union

import jsonref
from flake8.api import legacy as flake8
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError

from .errors import ProjectCardJSONSchemaError, ProjectCardValidationError, PycodeError
from .logger import CardLogger

ROOTDIR = Path(__file__).resolve().parent
PROJECTCARD_SCHEMA = ROOTDIR / "schema" / "projectcard.json"

# Errors to catch in valdiating "wrangler" project cards which use python code.
# E9 Runtime
# F63 undefined name name
# F823 local variable name ... referenced before assignment
# F405 name may be undefined, or defined from star imports: module
FLAKE8_ERRORS = ["E9", "F821", "F823", "F405"]


def _open_json(schema_path: Path) -> dict:
    try:
        with schema_path.open() as file:
            _json = json.loads(file.read())
            return _json
    except FileNotFoundError as err:
        msg = "Schema not found."
        CardLogger.error(msg + f"\n{schema_path}")
        raise ProjectCardJSONSchemaError(msg) from FileNotFoundError
    except JSONDecodeError as err:
        msg = "Schema not valid JSON."
        CardLogger.error(msg + f"\n{schema_path}")
        raise ProjectCardJSONSchemaError(msg) from err


def _load_schema(schema_absolute_path: Path) -> dict:
    base_path = Path(schema_absolute_path).parent
    base_uri = f"file:///{base_path}/"

    if not schema_absolute_path.exists():
        msg = f"Schema not found at {schema_absolute_path}"
        CardLogger.error(msg)
        raise FileNotFoundError(msg)

    _s = jsonref.replace_refs(
        _open_json(schema_absolute_path),
        base_uri=base_uri,
        jsonschema=True,
        lazy_load=False,
    )

    # CardLogger.debug(f"----\n{schema_absolute_path}\n{_s}")
    return _s


def package_schema(
    schema_path: Union[Path, str] = PROJECTCARD_SCHEMA,
    outfile_path: Optional[Union[Path, str]] = None,
) -> None:
    """Consolidates referenced schemas into a single schema and writes it out.

    Args:
        schema_path: Schema to read int and package. Defaults to PROJECTCARD_SCHEMA which is
             ROOTDIR / "schema" / "projectcard.json".
        outfile_path: Where to write out packaged schema. Defaults
            to schema_path.basepath.packaged.json
    """
    schema_path = Path(schema_path)
    _s_data = _load_schema(schema_path)
    default_outfile_path = schema_path.parent / f"{schema_path.stem}packaged.{schema_path.suffix}"
    outfile_path = outfile_path or default_outfile_path
    outfile_path = Path(outfile_path)
    with outfile_path.open("w") as outfile:
        json.dump(_s_data, outfile, indent=4)
    CardLogger.info(f"Wrote {schema_path.stem} to {outfile_path.stem}")


def validate_schema_file(schema_path: Path = PROJECTCARD_SCHEMA) -> bool:
    """Validates that a schema file is a valid JSON-schema.

    Args:
        schema_path: _description_. Defaults to PROJECTCARD_SCHEMA which is
            ROOTDIR / "schema" / "projectcard.json".
    """
    try:
        _schema_data = _load_schema(schema_path)
        # _resolver = _ref_resolver(schema_path,_schema_data)
        validate({}, schema=_schema_data)  # ,resolver=_resolver)
    except ValidationError:
        pass
    except SchemaError as e:
        CardLogger.error(e)
        raise ProjectCardJSONSchemaError from e

    return True


def update_dict_with_schema_defaults(
    data: dict, schema: Union[Path, dict] = PROJECTCARD_SCHEMA
) -> dict:
    """Recursively update missing required properties with default values.

    Args:
        data: The data dictionary to update.
        schema: The schema dictionary or path to the schema file.

    Returns:
        The updated data dictionary.
    """
    if isinstance(schema, (str, Path)):
        schema = _load_schema(schema)

    if "properties" in schema:
        for prop_name, schema_part in schema["properties"].items():
            # Only update if the property is required, has a default, and is not already there
            if (
                prop_name not in data
                and "default" in schema_part
                and prop_name in schema.get("required", [])
            ):
                CardLogger.debug(f"Adding default value for {prop_name}: {schema_part['default']}")
                data[prop_name] = schema_part["default"]
            elif (
                prop_name in data
                and isinstance(data[prop_name], dict)
                and "properties" in schema_part
            ):
                data[prop_name] = update_dict_with_schema_defaults(data[prop_name], schema_part)
            elif (
                prop_name in data and isinstance(data[prop_name], list) and "items" in schema_part
            ):
                for item in data[prop_name]:
                    if isinstance(item, dict):
                        update_dict_with_schema_defaults(item, schema_part["items"])
    return data


def validate_card(
    jsondata: dict, schema_path: Path = PROJECTCARD_SCHEMA, parse_defaults: bool = True
) -> bool:
    """Validates json-like data to specified schema.

    If `pycode` key exists, will evaluate it for basic runtime errors using Flake8.
    Note: will not flag any invalid use of RoadwayNetwork or TransitNetwork APIs.

    Args:
        jsondata: json-like data to validate.
        schema_path: path to schema to validate to.
            Defaults to PROJECTCARD_SCHEMA which is
            ROOTDIR / "schema" / "projectcard.json"
        parse_defaults: if True, will use default values for missing required attributes.

    Raises:
        ValidationError: If jsondata doesn't conform to specified schema.
        SchemaError: If schema itself is not valid.
    """
    if "project" in jsondata:
        CardLogger.debug(f"Validating: {jsondata['project']}")
    try:
        _schema_data = _load_schema(schema_path)
        if parse_defaults:
            jsondata = update_dict_with_schema_defaults(jsondata, _schema_data)
        validate(jsondata, schema=_schema_data)
    except ValidationError as e:
        CardLogger.error(f"---- Error validating {jsondata['project']} ----")
        msg = f"\nRelevant schema: {e.schema}\nValidator Value: {e.validator_value}\nValidator: {e.validator}"
        msg += f"\nabsolute_schema_path:{e.absolute_schema_path}\nabsolute_path:{e.absolute_path}"
        CardLogger.error(msg)
        raise ProjectCardValidationError from e
    except SchemaError as e:
        CardLogger.error(e)
        raise ProjectCardJSONSchemaError from e

    if "pycode" in jsondata:
        if "self." in jsondata["pycode"] and "self_obj_type" not in jsondata:
            msg = "If using self, must specify what `self` refers to in yml frontmatter using self_obj_type: <RoadwayNetwork|TransitNetwork>"
            raise PycodeError(msg)
        _validate_pycode(jsondata)

    return True


DEFAULT_MOCKED_VARS = ["self", "roadway_net", "transit_net"]


def _validate_pycode(jsondata: dict, mocked_vars: list[str] = DEFAULT_MOCKED_VARS) -> None:
    """Use flake8 to evaluate basic runtime errors on pycode.

    Uses mock.MagicMock() for self to mimic RoadwayNetwork or TransitNetwork
    Limitation: will not fail on invalid use of RoadwayNetwork or TransitNetwork APIs

    Args:
        jsondata: project card json data as a python dictionary
        mocked_vars: list of variables available in the execution of the code
    """
    style_guide = flake8.get_style_guide(select=FLAKE8_ERRORS, ignore=["E", "F", "W"])
    dir = TemporaryDirectory()
    tmp_py_path = Path(dir.name) / "tempcode.py"
    CardLogger.debug(f"Storing temporary python files at: {tmp_py_path!s}")

    # Add self, transit_net and roadway_net as mocked elements
    py_file_contents = "import mock\n"
    py_file_contents += "\n".join([f"{v} = mock.Mock()" for v in mocked_vars])
    py_file_contents += "\n" + jsondata["pycode"]

    with tmp_py_path.open("w") as py_file:
        py_file.write(py_file_contents)

    report = style_guide.check_files([tmp_py_path])

    if report.total_errors:
        CardLogger.error(f"Errors found in {jsondata['project']}")
        CardLogger.debug(f"FILE CONTENTS\n{py_file_contents}")
        errors = {c: report.get_statistics(c) for c in FLAKE8_ERRORS if report.get_statistics(c)}
        CardLogger.debug(f"Flake 8 Report:\n {errors}")
        msg = f"Found {report.total_errors} errors in {jsondata['project']}"
        raise PycodeError(msg)
    dir.cleanup()
