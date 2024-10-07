"""Functions for mkdocs documentation."""

import logging
import os
import re
from pathlib import Path

from projectcard import ProjectCard
from projectcard.utils import slug_to_str

SCHEMA_DIR = Path("projectcard") / "schema"


def define_env(env):
    """This is the hook for defining variables, macros and filters.

    - variables: the dictionary that contains the environment variables
    - macro: a decorator function, to declare a macro.
    """

    @env.macro
    def document_schema(schema_filename: str) -> str:
        from json_schema_for_humans.generate import generate_from_schema
        from json_schema_for_humans.generation_configuration import (
            GenerationConfiguration,
        )

        _rel_schema_path = SCHEMA_DIR / schema_filename
        _abs_schema_path = _rel_schema_path.absolute()
        if not _abs_schema_path.exists():
            msg = f"Schema doesn't exist at: {_abs_schema_path}"
            raise FileNotFoundError(msg)

        _config = GenerationConfiguration(
            minify=False,
            copy_css=False,
            copy_js=False,
            template_name="js",
            expand_buttons=True,
        )

        content = generate_from_schema(_abs_schema_path, config=_config)

        # get content ready for mkdocs
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

    def _categories_as_str(card: ProjectCard) -> str:
        if len(card.change_types) == 1:
            return slug_to_str(card.change_type)

        _cat_str = "Multiple: "
        _cat_str += ", ".join([f"{slug_to_str(c)}" for c in list(set(card.change_types))])
        return _cat_str

    def _card_to_md(card: ProjectCard) -> str:
        with Path(card.file).open("r") as file:
            file_txt = file.read_text()
        _card_md = f"\n###{card.project.title()}\n\n"
        _card_md += f"**Category**: {_categories_as_str(card)}\n"
        _card_md += f'``` yaml title="examples/{Path(card.file).name}"\n\n'
        _card_md += file_txt
        _card_md += "\n```\n"
        return _card_md

    @env.macro
    def list_examples(data_dir: Path) -> str:
        """Outputs a simple list of the directories in a folder in markdown.

        Args:
            data_dir: directory to search in
        Returns: markdown-formatted list
        """
        from projectcard.io import _make_slug, read_cards

        table_fields = ["Category", "Notes"]

        data_dir = Path(env.project_dir) / data_dir

        _md_examples = "\n## Cards\n"
        _md_table = (
            "| **Name** | **"
            + "** | **".join(table_fields)
            + "** |\n| "
            + " ----- | " * (len(table_fields) + 1)
            + "\n"
        )

        def _card_to_mdrow(card):
            _md_row = (
                f"| [{card.project.title()}](#{_make_slug(card.project).replace('_','-')}) | "
            )
            _md_row += f" {_categories_as_str(card)} |"
            _md_row += f" {card.notes} |\n"
            return _md_row

        _example_cards = None
        _example_cards = read_cards(data_dir)

        for _card in _example_cards.values():
            _md_table += _card_to_mdrow(_card)
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
