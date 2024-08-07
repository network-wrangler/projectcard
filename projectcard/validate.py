"""Validates ProjectCard JSON data against a JSON schema."""

import json
from json import JSONDecodeError
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Union

import jsonref
from flake8.api import legacy as flake8
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError

from .logger import CardLogger

ROOTDIR = Path(__file__).resolve().parent
PROJECTCARD_SCHEMA = ROOTDIR / "schema" / "projectcard.json"

# Errors to catch in valdiating "wrangler" project cards which use python code.
# E9 Runtime
# F63 undefined name name
# F823 local variable name ... referenced before assignment
# F405 name may be undefined, or defined from star imports: module
FLAKE8_ERRORS = ["E9", "F821", "F823", "F405"]


class ProjectCardValidationError(ValidationError):
    """Error in formatting of ProjectCard."""

    pass


class SubprojectValidationError(ProjectCardValidationError):
    """Error in formatting of Subproject."""

    pass


class PycodeError(ProjectCardValidationError):
    """Basic runtime error in python code."""

    pass


class ProjectCardJSONSchemaError(SchemaError):
    """Error in the ProjectCard json schema."""

    pass


def _open_json(schema_path: str) -> dict:
    try:
        with open(schema_path, "r") as file:
            _json = json.loads(file.read())
            return _json
    except FileNotFoundError:
        CardLogger.error(f"Schema not found: {schema_path}")
        raise ProjectCardJSONSchemaError("Schema definition missing")
    except JSONDecodeError:
        CardLogger.error(f"Schema not valid JSON: {schema_path}")
        raise ProjectCardJSONSchemaError("Schema definition invalid")


def _load_schema(schema_absolute_path: Union[Path, str]) -> dict:
    base_path = Path(schema_absolute_path).parent
    base_uri = f"file:///{base_path}/"

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
    outfile_path: Union[Path, str] = None,
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
    if outfile_path is None:
        outfile_path = schema_path.parent / f"{schema_path.stem}packaged.{schema_path.suffix}"
    outfile_path = Path(outfile_path)
    with open(outfile_path, "w") as outfile:
        json.dump(_s_data, outfile, indent=4)
    CardLogger.info(f"Wrote {schema_path.stem} to {outfile_path.stem}")


def validate_schema_file(schema_path: Union[Path, str] = PROJECTCARD_SCHEMA) -> bool:
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
        raise ProjectCardJSONSchemaError(f"{e}")

    return True


def validate_card(jsondata: dict, schema_path: Union[str, Path] = PROJECTCARD_SCHEMA) -> bool:
    """Validates json-like data to specified schema.

    If `pycode` key exists, will evaluate it for basic runtime errors using Flake8.
    Note: will not flag any invalid use of RoadwayNetwork or TransitNetwork APIs.

    Args:
        jsondata: json-like data to validate.
        schema_path: path to schema to validate to.
            Defaults to PROJECTCARD_SCHEMA which is
            ROOTDIR / "schema" / "projectcard.json"

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
        msg = f"\nRelevant schema: {e.schema}\nValidator Value: {e.validator_value}\nValidator: {e.validator}"
        msg += f"\nabsolute_schema_path:{e.absolute_schema_path}\nabsolute_path:{e.absolute_path}"
        CardLogger.error(msg)
        raise ProjectCardValidationError(f"{e}")
    except SchemaError as e:
        CardLogger.error(e)
        raise ProjectCardJSONSchemaError(f"{e}")

    if "pycode" in jsondata:
        if "self." in jsondata["pycode"]:
            if "self_obj_type" not in jsondata:
                raise PycodeError(
                    "If using self, must specify what `self` refers to in yml frontmatter using self_obj_type: <RoadwayNetwork|TransitNetwork>"
                )
        _validate_pycode(jsondata)

    return True


def _validate_pycode(
    jsondata: dict, mocked_vars: List[str] = ["self", "roadway_net", "transit_net"]
) -> None:
    """Use flake8 to evaluate basic runtime errors on pycode.

    Uses mock.MagicMock() for self to mimic RoadwayNetwork or TransitNetwork
    Limitation: will not fail on invalid use of RoadwayNetwork or TransitNetwork APIs

    Args:
        jsondata: project card json data as a python dictionary
        mocked_vars: list of variables available in the execution of the code
    """
    style_guide = flake8.get_style_guide(select=FLAKE8_ERRORS, ignore=["E", "F", "W"])
    dir = TemporaryDirectory()
    tmp_py_path = str(Path(dir.name) / "tempcode.py")
    CardLogger.debug(f"Storing temporary python files at: {tmp_py_path}")

    # Add self, transit_net and roadway_net as mocked elements
    py_file_contents = "import mock\n"
    py_file_contents += "\n".join([f"{v}=mock.Mock()" for v in mocked_vars])
    py_file_contents += "\n" + jsondata["pycode"]

    with open(tmp_py_path, "w") as py_file:
        py_file.write(py_file_contents)

    report = style_guide.check_files([tmp_py_path])

    if report.total_errors:
        CardLogger.error(f"Errors found in {jsondata['project']}")
        CardLogger.debug(f"FILE CONTENTS\n{py_file_contents}")
        errors = {c: report.get_statistics(c) for c in FLAKE8_ERRORS if report.get_statistics(c)}
        CardLogger.debug(f"Flake 8 Report:\n {errors}")
        raise PycodeError(f"Found {report.total_errors} errors in {jsondata['project']}")
    dir.cleanup()
