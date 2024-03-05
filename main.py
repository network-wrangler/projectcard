import logging
import os
import re
from pathlib import Path

from projectcard import ProjectCard

SCHEMA_DIR = "schema"


def define_env(env):
    """
    This is the hook for defining variables, macros and filters

    - variables: the dictionary that contains the environment variables
    - macro: a decorator function, to declare a macro.
    """

    @env.macro
    def document_schema(schema_filename: str) -> str:
        import json

        from json_schema_for_humans.generate import generate_from_schema
        from json_schema_for_humans.generation_configuration import (
            GenerationConfiguration,
        )

        _rel_schema_path = os.path.join(SCHEMA_DIR, schema_filename)
        _abs_schema_path = Path(_rel_schema_path).absolute()
        if not os.path.exists(_abs_schema_path):
            raise ValueError(f"Schema doesn't exist at: {_abs_schema_path}")

        _config = GenerationConfiguration(
            minify=False,
            copy_css=False,
            copy_js=False,
            template_name="js",
            expand_buttons=True,
        )

        content = generate_from_schema(_abs_schema_path, config=_config)

        ### get content ready for mkdocs
        _footer = _get_html_between_tags(content, tag="footer")
        replace_strings = {
            "<!DOCTYPE html>": "",
            '<div class="breadcrumbs"></div><span class="badge badge-dark value-type">\
            Type: object</span><br/>': "",
        }

        for _orig, _new in replace_strings.items():
            content = content.replace(_orig, _new)

        content = _get_html_between_tags(content, tag="body")
        content = _rm_html_between_tags(content, tag="footer")
        return content

    @env.macro
    def include_file(filename: str, downshift_h1=True, start_line: int = 0, end_line: int = None):
        """
        Include a file, optionally indicating start_line and end_line.

        Will create redirects if specified in FIND_REPLACE in main.py.

        args:
            filename: file to include, relative to the top directory of the documentation project.
            downshift_h1: If true, will downshift headings by 1 if h1 heading found.
                Defaults to True.
            start_line (Optional): if included, will start including the file from this line
                (indexed to 0)
            end_line (Optional): if included, will stop including at this line (indexed to 0)
        """
        logging.info(f"Including file: {filename}")
        full_filename = os.path.join(env.project_dir, filename)
        with open(full_filename, "r") as f:
            lines = f.readlines()
        line_range = lines[start_line:end_line]
        content = "".join(line_range)

        # Downshift headings if h1 found
        md_heading_re = {
            1: re.compile(r"(#{1}\s)(.*)"),
            2: re.compile(r"(#{2}\s)(.*)"),
            3: re.compile(r"(#{3}\s)(.*)"),
            4: re.compile(r"(#{4}\s)(.*)"),
            5: re.compile(r"(#{5}\s)(.*)"),
        }

        if md_heading_re[1].search(content) and downshift_h1:
            content = re.sub(md_heading_re[5], r"#\1\2", content)
            content = re.sub(md_heading_re[4], r"#\1\2", content)
            content = re.sub(md_heading_re[3], r"#\1\2", content)
            content = re.sub(md_heading_re[2], r"#\1\2", content)
            content = re.sub(md_heading_re[1], r"#\1\2", content)

        return content

    def _categories_as_str(card: "ProjectCard") -> str:
        _change_types = [
            "roadway_deletion",
            "roadway_addition",
            "roadway_managed_lanes",
            "roadway_property_change",
        ]
        _cats = [c for c in card.__dict__ if c in _change_types]
        if _cats:
            return _cats[0]

        if len(card.__dict__["changes"]) == 1:
            _cats = [c for c in card.__dict__["changes"] if c in _change_types]
            return _cats[0]

        _cat_str = "Multiple Change Categories:<ul>\n"
        _cats = [c for c in card.__dict__["changes"] if c in _change_types]
        _cat_str += "".join([f"<li>{c}</li>\n" for c in _cats])
        _cat_str += "</ul>"

    def _card_to_md(card: "ProjectCard") -> str:
        _card_md = f"\n###{card.project}\n\n"
        _card_md += f"**Category**: {_categories_as_str(card)}\n"
        _card_md += "```yml\n\n"
        _card_md += include_file((card.__dict__["file"]), downshift_h1=False)
        _card_md += "\n```\n"
        return _card_md

    @env.macro
    def list_examples(data_dir: str) -> str:
        """Outputs a simple list of the directories in a folder in markdown.
        Args:
            data_dir (str):directory to search in
        Returns:
            str: markdown-formatted list
        """
        from projectcard.io import _make_slug, read_cards

        table_fields = ["Category"]

        data_dir = os.path.join(env.project_dir, data_dir)

        _md_examples = f"\n## Cards\n"
        _md_table = (
            "| **Name** | "
            + "** | **".join(table_fields)
            + " |\n| "
            + " ----- | " * (len(table_fields) + 1)
            + "\n"
        )

        def _card_to_mdrow(card, fields):
            _md_row = f"| [{card.project}](#{_make_slug(card.project).replace('_','-')}) | "
            _md_row += f"{_categories_as_str(card)}" " |\n"
            return _md_row

        _example_cards = read_cards(data_dir)

        for _card in _example_cards.values():
            _md_table += _card_to_mdrow(_card, table_fields)
            _md_examples += _card_to_md(_card)

        example_md = _md_table + _md_examples

        return example_md


def _get_html_between_tags(content: str, tag: str = "body") -> str:
    """Returns string that is between tags if they are found. If not, returns whole string.

    Args:
        content (str): Content
        tag: tag to get content for. Note if multiple sets of the tag extist, will return the
            first set of content wrapped by the tag if the tag exists. Defaults to "body" tag.
    """
    if f"</{tag}>" not in content:
        return content
    content = content[content.index(f"<{tag}") :]
    content = content[content.index(">") :]

    content = content[: content.index(f"</{tag}>")]
    return content


def _rm_html_between_tags(content: str, tag: str = "footer") -> str:
    """Returns string without the tags if they are found. If not, returns whole string.
    Only removes first found instance.

    Args:
        content (str): Content
        tag: tag to get content for. Note if multiple sets of the tag extist, will return the
            first set of content wrapped by the tag if the tag exists. Defaults to "body" tag.
    """
    if f"</{tag}>" not in content:
        return content

    content_a, content_b = content.split(f"<{tag}", 1)
    content_b, content_c = content_b.split(f"</{tag}>", 1)

    return content_a + content_c
