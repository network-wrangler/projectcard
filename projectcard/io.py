"""Functions for reading and writing project cards."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable, Collection, Mapping, Union

import toml
import yaml

from .logger import CardLogger
from .projectcard import REPLACE_KEYS, VALID_EXT, ProjectCard


class ProjectCardReadError(Exception):
    """Error in reading project card."""

    pass


SKIP_READ = ["valid"]
SKIP_WRITE = ["valid"]


def _get_cardpath_list(filepath, valid_ext: Collection[str] = VALID_EXT, recursive: bool = False):
    """Returns a list of valid paths to project cards given a search string.

    Args:
        filepath: where the project card is.  A single path, list of paths,
            a directory, or a glob pattern.
        valid_ext: list of valid file extensions
        recursive: if True, will search recursively in subdirs

    Returns: list of valid paths to project cards
    """
    CardLogger.debug(f"Getting cardpath list: {filepath} of type {type(filepath)}")
    if isinstance(filepath, list):
        CardLogger.debug(f"Reading list of paths: {filepath}")
        if not all(Path(f).is_file() for f in filepath):
            _missing = [f for f in filepath if not Path(f).is_file()]
            raise FileNotFoundError(f"{_missing} is/are not a file/s")
        _paths = [Path(f) for f in filepath]
    elif (isinstance(filepath, Path) or isinstance(filepath, str)) and Path(filepath).is_dir():
        CardLogger.debug(f"Getting all files in: {filepath}")
        if recursive:
            _paths = [Path(p) for p in Path(filepath).rglob("*") if p.is_file()]
        else:
            _paths = [Path(p) for p in Path(filepath).glob("*")]
    else:
        raise ProjectCardReadError(f"filepath: {filepath} not understood.")
    CardLogger.debug(f"All paths: {_paths}")
    _card_paths = [p for p in _paths if p.suffix in valid_ext]
    CardLogger.debug(f"Reading set of paths: {_card_paths}")
    return _card_paths


def _read_yml(filepath: str) -> dict:
    CardLogger.debug(f"Reading YML: {filepath}")
    with open(filepath, "r") as cardfile:
        attribute_dictionary = yaml.safe_load(cardfile.read())
    return attribute_dictionary


def _read_toml(filepath: str) -> dict:
    CardLogger.debug(f"Reading TOML: {filepath}")
    with open(filepath, "r", encoding="utf-8") as cardfile:
        attribute_dictionary = toml.load(cardfile.read())
    return attribute_dictionary


def _read_json(filepath: str) -> dict:
    CardLogger.debug(f"Reading JSON: {filepath}")
    with open(filepath, "r") as cardfile:
        attribute_dictionary = json.loads(cardfile.read())
    return attribute_dictionary


def _read_wrangler(filepath: str) -> dict:
    CardLogger.debug(f"Reading Wrangler: {filepath}")
    with open(filepath, "r") as cardfile:
        delim = cardfile.readline()
        _yaml, _pycode = cardfile.read().split(delim)

    attribute_dictionary = yaml.safe_load(_yaml)
    attribute_dictionary["pycode"] = _pycode.lstrip("\n")

    return attribute_dictionary


def write_card(project_card, filename: str = None):
    """Writes project card dictionary to YAML file."""
    if not filename:
        filename = _make_slug(project_card.project) + ".yml"
    if not project_card.valid:
        CardLogger.warning(f"{project_card.project} Project Card not valid.")
    out_dict = {}

    # Writing these first manually so that they are at top of file
    out_dict["project"] = None
    if project_card.dict.get("tags"):
        out_dict["tags"] = None
    if project_card.dict.get("dependencies"):
        out_dict["dependencies"] = None
    out_dict.update(project_card.dict)
    for k in SKIP_WRITE:
        if k in out_dict:
            del out_dict[k]

    with open(filename, "w") as outfile:
        yaml.dump(out_dict, outfile, default_flow_style=False, sort_keys=False)

    CardLogger.info("Wrote project card to: {}".format(filename))


def _make_slug(text, delimiter: str = "_"):
    """Makes a slug from text."""
    import re

    text = re.sub("[,.;@#?!&$']+", "", text.lower())
    return re.sub("[\ ]+", delimiter, text)


def _replace_selected(txt: str, change_dict: dict = REPLACE_KEYS):
    """Will returned uppercased text if matches a select set of values.

    Otherwise returns same text.

    Args:
        txt: string
        change_dict: dictionary of key value pairs to replace
    """
    return change_dict.get(txt, txt)


def _change_keys(obj: dict, convert: Callable = _replace_selected) -> dict:
    """Recursively goes through the dictionary obj and replaces keys with the convert function.

    Args:
        obj: dictionary object to convert keys of
        convert: convert function from one to other

    Source: https://stackoverflow.com/questions/11700705/how-to-recursively-replace-character-in-keys-of-a-nested-dictionary
    """
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[convert(k)] = _change_keys(v, convert)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(_change_keys(v, convert) for v in obj)
    else:
        return obj
    return new


_read_method_map = {
    ".yml": _read_yml,
    ".yaml": _read_yml,
    ".json": _read_json,
    ".toml": _read_toml,
    ".wr": _read_wrangler,
    ".wrangler": _read_wrangler,
}


def read_card(filepath: str, validate: bool = False):
    """Read single project card from a path and return project card object.

    Args:
        filepath: file where the project card is.
        validate: if True, will validate the project card schemea
    """
    if not Path(filepath).is_file():
        raise FileNotFoundError(f"Cannot find project card file: {filepath}")
    card_dict = read_cards(filepath, _cards={})
    card = list(card_dict.values())[0]
    if validate:
        assert card.valid
    return card


def read_cards(
    filepath: Union[Collection[str], str],
    filter_tags: Collection[str] = [],
    recursive: bool = False,
    _cards: Mapping[str, ProjectCard] = {},
) -> Mapping[str, ProjectCard]:
    """Reads collection of project card files by inferring the file type.

    Lowercases all keys, but then replaces any that need to be uppercased using the
    REPLACE_KEYS mapping.  Needed to keep "A" and "B" uppercased.

    Args:
        filepath: where the project card is.  A single path, list of paths,
            a directory, or a glob pattern.
        filter_tags: list of tags to filter by.
        recursive: if True, will search recursively in subdirs.
        _cards: dictionary of project cards to add to. Should not be used by user.

    Returns: dictionary of project cards by project name
    """
    CardLogger.debug(f"Reading cards from {filepath}.")

    filter_tags = list(map(str.lower, filter_tags))
    if isinstance(filepath, list) or not os.path.isfile(filepath):
        _card_paths = _get_cardpath_list(
            filepath, valid_ext=_read_method_map.keys(), recursive=recursive
        )
        for p in _card_paths:
            _cards.update(read_cards(p, filter_tags=filter_tags, _cards=_cards))
        return _cards

    _ext = os.path.splitext(filepath)[1]
    if _ext not in _read_method_map.keys():
        CardLogger.debug(f"Unsupported file type for file {filepath}")
        raise ProjectCardReadError(f"Unsupported file type: {_ext}")
    _card_dict = _read_method_map[_ext](filepath)
    for k in SKIP_READ:
        if k in _card_dict:
            del _card_dict[k]
    _card_dict = {k: v for k, v in _card_dict.items() if v is not None}
    _card_dict = _change_keys(_card_dict)
    _card_dict["file"] = filepath
    _project_name = _card_dict["project"].lower()
    if _project_name in _cards:
        raise ProjectCardReadError(
            f"Names not unique from existing scenario projects: {_project_name}"
        )
    if filter_tags and set(list(map(str.lower, _card_dict.get("tags", [])))).isdisjoint(
        set(filter_tags)
    ):
        CardLogger.debug(f"Skipping {_project_name} - no overlapping tags with {filter_tags}.")
        return _cards
    _cards[_project_name] = ProjectCard(_card_dict)

    return _cards
