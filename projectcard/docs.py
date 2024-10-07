"""Utilities to assist in documentation which may be useful for other purposes."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .utils import slug_to_str, make_slug
from .io import read_cards


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


def _categories_as_str(change_types: list[str] ) -> str:
    if len(change_types) == 1:
        return slug_to_str(change_types[0])

    _cat_str = "Multiple: "
    _cat_str += ", ".join([f"{slug_to_str(c)}" for c in list(set(change_types))])
    return _cat_str


def _card_to_mdrow(card):
    _md_row = (
        f"| [{card.project.title()}](#{make_slug(card.project).replace('_','-')}) | "
    )
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