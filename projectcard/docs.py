"""Utilities to assist in documentation which may be useful for other purposes."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Union

import pandas as pd

from .io import read_cards
from .utils import make_slug, slug_to_str
from .validate import _open_json

if TYPE_CHECKING:
    from .projectcard import ProjectCard


def card_to_md(card: ProjectCard) -> str:
    """Convert a project card contents to markdown text inserted as yaml."""
    _card_md = f"\n###{card.project.title()}\n\n"
    _card_md += f"**Category**: {_categories_as_str(card.change_types)}\n"
    _card_md += f'``` yaml title="examples/{Path(card.file).name}"\n\n'
    _card_md += card.file.read_text()
    _card_md += "\n```\n"
    return _card_md


def _categories_as_str(change_types: list[str]) -> str:
    if len(change_types) == 1:
        return slug_to_str(change_types[0])

    _cat_str = "Multiple: "
    _cat_str += ", ".join([f"{slug_to_str(c)}" for c in list(set(change_types))])
    return _cat_str


def _card_to_mdrow(card):
    _md_row = f"| [{card.project.title()}](#{make_slug(card.project).replace('_','-')}) | "
    _md_row += f" {_categories_as_str(card.change_types)} |"
    _md_row += f" {card.notes} |\n"
    return _md_row


def card_list_to_table(card_dir: Path) -> str:
    """Generates a table of all project cards in a directory followed by the cards."""
    CARD_LIST_TABLE_FIELDS = ["Category", "Notes"]
    md_examples = "\n## Cards\n"
    md_table = (
        "| **Name** | **"
        + "** | **".join(CARD_LIST_TABLE_FIELDS)
        + "** |\n| "
        + " ----- | " * (len(CARD_LIST_TABLE_FIELDS) + 1)
        + "\n"
    )

    example_cards = read_cards(card_dir)

    for card in example_cards.values():
        md_table += _card_to_mdrow(card)
        md_examples += card_to_md(card)

    return md_table + md_examples


ROOTDIR = Path(__file__).resolve().parent
PROJECTCARD_SCHEMA = ROOTDIR / "schema" / "projectcard.json"


def json_schema_to_md(schema_path: Path = PROJECTCARD_SCHEMA) -> str:
    """Generate Markdown documentation for a JSON schema."""
    if not schema_path.is_absolute():
        rel_schema_path = ROOTDIR / schema_path
        schema_path = rel_schema_path.absolute()
    schema_dir = schema_path.parent
    schema_dict = _get_dict_of_schemas(schema_dir)
    sorted_folders = sorted(schema_dict.keys())
    markdown_output = f"{schema_path.root}\n"
    for rel_folder in sorted_folders:
        for schema_file in schema_dict[rel_folder]:
            markdown_output += _single_jsonschema_to_md(schema_file, rel_folder)

    return markdown_output


def _list_to_bullets(items: list, fmt: Literal["html", "md"] = "md") -> str:
    """Convert a list of items to a bulleted list in markdown or html."""
    if fmt == "html":
        return "<ul>" + "".join(f"<li>{json.dumps(item)}</li>" for item in items) + "\n</ul>"
    if fmt == "md":
        return "\n".join(f"- `{json.dumps(item)}`" for item in items)
    msg = "fmt must be 'html' or 'md'"
    raise ValueError(msg)


def _restrictions_to_md(item: dict, list_fmt: Literal["html", "md"] = "md") -> str:
    required_md = ""
    lb = "" if list_fmt == "html" else "\n\n"
    if "required" in item:
        required_md += (
            f"**Required:**{lb}"
            + _fmt_array_or_obj_or_str(item["required"], list_fmt=list_fmt)
            + f"{lb}"
        )
    if "anyOf" in item:
        required_md += (
            f"**Any Of:**{lb}"
            + _fmt_array_or_obj_or_str(item["anyOf"], list_fmt=list_fmt)
            + f"{lb}"
        )
    if "oneOf" in item:
        required_md += (
            f"**One Of:**{lb}"
            + _fmt_array_or_obj_or_str(item["oneOf"], list_fmt=list_fmt)
            + f"{lb}"
        )
    if "enum" in item:
        required_md += "**Enumeration:** `" + "`,`".join(list(map(str, item["enum"]))) + f"`{lb}"
    return required_md


def _properties_to_md(properties: dict) -> str:
    """Convert a dictionary of properties to a markdown table."""
    rows = []
    for prop, details in properties.items():
        prop_type = _get_type_txt(details)
        # Handle anyOf and oneOf
        row = {
            "Property": f"`{prop}`",
            "Type": prop_type,
            "Description": details.get(
                "description", details.get("title", details.get("name", "-"))
            ),
            "Restrictions": _restrictions_to_md(details),
        }
        rows.append(row)
    properties_df = pd.DataFrame(rows)
    properties_md = properties_df.to_markdown(index=False)
    return properties_md


def _defs_to_md(defs: dict) -> str:
    """Convert a dictionary of $defs to a markdown table with anchors."""
    rows = []
    defs_md = ""
    for def_name, details in defs.items():
        row = {
            "Definition": f"`{def_name}`",
            "Type": _get_type_txt(details),
            "Description": details.get("description", details.get("name", "-")),
            "Restrictions": _restrictions_to_md(details, list_fmt="html"),
        }
        rows.append(row)
        # anchor = def_name.replace('/', '_')
        # defs_md += f'<a name="{anchor}"></a>\n\n'
    defs_df = pd.DataFrame(rows)
    defs_md += defs_df.to_markdown(index=False)
    return defs_md


def _examples_to_md(examples: list, schema_name: str) -> str:
    """Convert a list of examples to markdown."""
    examples_md = ""
    indent = "    "
    if examples:
        for i, example in enumerate(examples, 1):
            examples_md += f'??? example "{schema_name} Example {i}"\n'
            examples_md += f"{indent}```json\n"
            examples_md += indent + json.dumps(example, indent=4).replace("\n", f"\n{indent}")
            examples_md += f"\n{indent}```\n"
    return examples_md


def _raw_schema_to_md(schema: dict, schema_name: str) -> str:
    """Convert a raw JSON schema to drop-down admonition."""
    raw_md = ""
    indent = "    "
    raw_md += f'??? abstract "{schema_name} Contents"\n'
    raw_md += f"{indent}```json\n"
    raw_md += indent + json.dumps(schema, indent=4).replace("\n", f"\n{indent}")
    raw_md += f"\n{indent}```\n"
    return raw_md


def _object_to_md(object_schema: dict, schema_name: str) -> str:
    """Convert json-schema object information to markdown."""
    defs = object_schema.get("$defs", {})
    properties = object_schema.get("properties", {})
    examples = object_schema.get("examples", [])
    SKIP = ["properties", "required", "oneOf", "anyOf", "$defs", "$schema", "examples", "type"]
    additional_info = {k: v for k, v in object_schema.items() if k not in SKIP}

    # Generate $defs table
    defs_md = ""
    if defs:
        defs_md = "\n**Definitions**:\n\n"
        defs_md += _defs_to_md(defs) + "\n\n"

    # Generate properties table
    properties_md = "\n**Properties**:\n\n" + _properties_to_md(properties)

    # Generate required fields list
    required_md = _restrictions_to_md(object_schema, list_fmt="html")

    # Generate examples
    examples_md = _examples_to_md(examples, schema_name) + "\n\n" if examples else ""

    # Generate additional information
    additional_md = ""
    if additional_info:
        additional_md = "**Additional Information**:\n\n"
        additional_md += _fmt_array_or_obj_or_str(additional_info)

    # Combine all parts
    object_md = f"\n*Type:* Object\n\n"
    if additional_md:
        object_md += additional_md + "\n\n"
    if defs_md:
        object_md += defs_md + "\n\n"
    object_md += properties_md + "\n\n"
    if required_md:
        object_md += required_md + "\n\n"
    if examples_md:
        object_md += examples_md + "\n\n"

    return object_md


def _get_type_txt(item: dict) -> str:
    if "items" in item:
        t = item["items"].get("type", item.get("$ref", "Any"))
        return f"`array` of `{t}` items."
    if "$ref" in item:
        return f"`{item['$ref']}`"
    return f"`{item.get('type', 'Any')}`"


def _fmt_array_or_obj_or_str(
    item: Union[dict, list, str], list_fmt: Literal["html", "md"] = "md"
) -> str:
    lb = "" if list_fmt == "html" else "\n\n"
    if isinstance(item, dict):
        if len(item) == 0:
            return ""
        if len(item) == 1:
            for k, v in item.items():
                if isinstance(v, list):
                    return f"{k}:{lb}{_list_to_bullets(v, fmt=list_fmt)}"
                return f"{k}: {v}"
        else:
            md = ""
            for k, v in item.items():
                if isinstance(v, list):
                    bullet_list = _list_to_bullets(v, fmt=list_fmt).replace("\n", "\n  ")
                    md += f"{k}:{lb} {bullet_list}"
                md += f"- {k}: {v}{lb}"
            return md
    elif isinstance(item, list):
        return _list_to_bullets(item, fmt=list_fmt)
    return str(item)


def _array_to_md(array_item: dict, schema_name: str) -> str:
    """Convert json-schema array information to markdown."""
    if "type" not in array_item or array_item["type"] != "array":
        return "Invalid array schema"

    array_md = f"\n*Type:* {_get_type_txt(array_item)}\n\n"

    SKIP = ["type", "$ref"]
    restrictions = {
        k: _fmt_array_or_obj_or_str(v)
        for k, v in array_item.get("items", {}).items()
        if k not in SKIP
    }
    if restrictions:
        array_md += "| Property | Value |\n"
        array_md += "|----------|-------|\n"
        for key, value in restrictions.items():
            array_md += f"| **{key}** | {value} |\n"
        array_md += "\n"

    # Handle $defs if present
    defs = array_item.get("$defs", {})
    if defs:
        array_md += f"\n**Definitions**:\n\n"
        array_md += _defs_to_md(defs) + "\n\n"

    # Generate examples
    examples = array_item.get("examples", [])
    examples_md = _examples_to_md(examples, schema_name) + "\n\n" if examples else ""
    if examples_md:
        array_md += examples_md + "\n\n"

    return array_md


def _other_type_to_md(schema_data, schema_name):
    content_md = f"Schema Type: {_get_type_txt(schema_data)}\n\n"

    # Generate additional information
    SKIP = [
        "properties",
        "required",
        "oneOf",
        "anyOf",
        "$defs",
        "$schema",
        "examples",
        "type",
        "enum",
    ]
    additional_info = {k: v for k, v in schema_data.items() if k not in SKIP}
    if additional_info:
        content_md = "**Additional Information**:\n\n"
        content_md += _fmt_array_or_obj_or_str(additional_info) + "\n\n"

    restrictions_md = _restrictions_to_md(schema_data, list_fmt="html")
    if restrictions_md:
        content_md += restrictions_md + "\n\n"

    # Handle $defs if present
    defs = schema_data.get("$defs", {})
    if defs:
        content_md += f"\n**Definitions**:\n\n"
        content_md += _defs_to_md(defs) + "\n\n"

    # Generate examples
    examples = schema_data.get("examples", [])
    if examples:
        examples_md = _examples_to_md(examples, schema_name) + "\n\n" if examples else ""
        content_md += examples_md + "\n\n"
    return content_md


def _single_jsonschema_to_md(schema_file: Path, rel_folder: Path) -> str:
    heading_level = len(rel_folder.parts) + 1  # +1 because base directory doesn't count
    header = "\n##"
    if heading_level > 1:
        header += f"{'#' * heading_level} {'.'.join(rel_folder.parts)}."
    header += f"{schema_file.name}\n"

    schema_data = _open_json(schema_file)
    schema_name = schema_data.get("title", f"`{schema_file.stem}`")

    # Determine the type of schema and call the appropriate function
    schema_type = schema_data.get("type", "unknown")
    if schema_type == "array":
        content_md = _array_to_md(schema_data, schema_name)
    elif schema_type == "object":
        content_md = _object_to_md(schema_data, schema_name)
    else:
        content_md = _other_type_to_md(schema_data, schema_name)

    content_md += "\n" + _raw_schema_to_md(schema_data, schema_name) + "\n"

    return header + content_md


def _get_dict_of_schemas(base_dir: Path, extension: str = ".json") -> defaultdict:
    base_dir = Path(base_dir)

    files_by_folder = defaultdict(list)
    for schema_file in base_dir.rglob(f"*{extension}"):
        files_by_folder[schema_file.parent.relative_to(base_dir)].append(schema_file)
    return files_by_folder
