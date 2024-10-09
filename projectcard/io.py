"""Functions for reading and writing project cards."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Optional, Union

import toml
import yaml

from .errors import ProjectCardReadError
from .logger import CardLogger
from .projectcard import REPLACE_KEYS, VALID_EXT, ProjectCard

ProjectCardFilepath = Union[Path, str]
ProjectCardFilepaths = Union[Path, list[Path], str, list[str]]

DEFAULT_BASE_PATH = Path.cwd()

SKIP_READ = ["valid"]
SKIP_WRITE = ["valid"]


def _get_cardpath_list(
    filepath: ProjectCardFilepaths, valid_ext: list[str] = VALID_EXT, recursive: bool = False
):
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
            msg = f"{_missing} is/are not a file/s"
            raise FileNotFoundError(msg)
        _paths = [Path(f) for f in filepath]
    elif (isinstance(filepath, (Path, str))) and Path(filepath).is_dir():
        CardLogger.debug(f"Getting all files in: {filepath}")
        if recursive:
            _paths = [Path(p) for p in Path(filepath).rglob("*") if p.is_file()]
        else:
            _paths = [Path(p) for p in Path(filepath).glob("*")]
    else:
        msg = f"filepath: {filepath} not understood."
        raise ProjectCardReadError(msg)
    CardLogger.debug(f"All paths: {_paths}")
    _card_paths = [p for p in _paths if p.suffix in valid_ext]
    CardLogger.debug(f"Reading set of paths: {_card_paths}")
    return _card_paths


def _read_yml(filepath: Path) -> dict:
    CardLogger.debug(f"Reading YML: {filepath}")
    with filepath.open("r") as cardfile:
        attribute_dictionary = yaml.safe_load(cardfile.read())
    return attribute_dictionary


def _read_toml(filepath: Path) -> dict:
    CardLogger.debug(f"Reading TOML: {filepath}")
    with filepath.open("r", encoding="utf-8") as cardfile:
        attribute_dictionary = toml.load(cardfile.read())
    return attribute_dictionary


def _read_json(filepath: Path) -> dict:
    CardLogger.debug(f"Reading JSON: {filepath}")
    with filepath.open("r") as cardfile:
        attribute_dictionary = json.loads(cardfile.read())
    return attribute_dictionary


def _read_wrangler(filepath: Path) -> dict:
    CardLogger.debug(f"Reading Wrangler: {filepath}")
    with filepath.open() as cardfile:
        delim = cardfile.readline()
        _yaml, _pycode = cardfile.read().split(delim)

    attribute_dictionary = yaml.safe_load(_yaml)
    attribute_dictionary["pycode"] = _pycode.lstrip("\n")

    return attribute_dictionary


def write_card(project_card, filename: Optional[Path] = None):
    """Writes project card dictionary to YAML file."""
    from .utils import make_slug

    default_filename = make_slug(project_card.project) + ".yml"
    filename = filename or Path(default_filename)

    if not project_card.valid:
        CardLogger.warning(f"{project_card.project} Project Card not valid.")
    out_dict: dict[str, Any] = {}

    # Writing these first manually so that they are at top of file
    out_dict["project"] = None
    if project_card.to_dict.get("tags"):
        out_dict["tags"] = None
    if project_card.to_dict.get("dependencies"):
        out_dict["dependencies"] = None
    out_dict.update(project_card.to_dict)
    for k in SKIP_WRITE:
        if k in out_dict:
            del out_dict[k]

    yaml_content = dict_to_yaml_with_comments(out_dict)

    with filename.open("w") as outfile:
        outfile.write(yaml_content)

    CardLogger.info(f"Wrote project card to: {filename}")


def dict_to_yaml_with_comments(d):
    """Converts a dictionary to a YAML string with comments."""
    yaml_str = yaml.dump(d, default_flow_style=False, sort_keys=False)
    yaml_lines = yaml_str.splitlines()
    final_yaml_lines = []

    for line in yaml_lines:
        if "#" in line:
            final_yaml_lines.append(f"#{line}")
        else:
            final_yaml_lines.append(line)

    return "\n".join(final_yaml_lines)


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

VALID_EXT = list(_read_method_map.keys())


def read_card(filepath: ProjectCardFilepath, validate: bool = False):
    """Read single project card from a path and return project card object.

    Args:
        filepath: file where the project card is.
        validate: if True, will validate the project card schemea
    """
    if not Path(filepath).is_file():
        msg = f"Cannot find project card file: {filepath}"
        raise FileNotFoundError(msg)
    card_dict = read_cards(filepath)
    card = next(iter(card_dict.values()))
    if validate:
        card.validate()
    return card


def _read_card(
    filepath: Path,
    filter_tags: Optional[list[str]] = None,
    existing_projects: Optional[list[str]] = None,
) -> Union[None, ProjectCard]:
    """Reads a single project card file and returns a ProjectCard object."""
    if filepath.suffix not in VALID_EXT:
        CardLogger.debug(f"Unsupported file type for file {filepath}")
        msg = f"Unsupported file type: {filepath.suffix}"
        raise ProjectCardReadError(msg)
    card_dict = _read_method_map[filepath.suffix](filepath)
    for k in SKIP_READ:
        if k in card_dict:
            del card_dict[k]
    card_dict = {k: v for k, v in card_dict.items() if v is not None}
    card_dict = _change_keys(card_dict)
    card_dict["file"] = filepath
    if existing_projects and card_dict["project"] in existing_projects:
        msg = f"Project name not unique from `existing_projects`: {card_dict['project']}"
        raise ProjectCardReadError(msg)
    if filter_tags and _overlapping_tags(card_dict["tags"], filter_tags):
        CardLogger.debug(
            f"Skipping {card_dict['project']} - no overlapping tags with {filter_tags}."
        )
        return None
    return ProjectCard(card_dict)


def _overlapping_tags(tags: list[str], filter_tags: list[str]) -> bool:
    """Checks if tags overlap."""
    return bool(set(map(str.lower, tags)).isdisjoint(set(filter_tags)))


def read_cards(
    filepath: ProjectCardFilepaths,
    filter_tags: Optional[list[str]] = None,
    recursive: bool = False,
    base_path: Path = DEFAULT_BASE_PATH,
    existing_projects: Optional[list[str]] = None,
) -> dict[str, ProjectCard]:
    """Reads collection of project card files by inferring the file type.

    Lowercases all keys, but then replaces any that need to be uppercased using the
    REPLACE_KEYS mapping.  Needed to keep "A" and "B" uppercased.

    If a path is given as a relative path, it will be resolved to an absolute path using
    the base_path.

    Args:
        filepath: where the project card is.  A single path, list of paths,
            a directory, or a glob pattern.
        filter_tags: list of tags to filter by.
        recursive: if True, will search recursively in subdirs.
        base_path: base path to resolve relative paths from. Defaults to current working directory.
        existing_projects: list of existing project names to check for uniqueness.

    Returns: dictionary of project cards by project name
    """
    CardLogger.debug(f"Reading cards from {filepath}.")
    filter_tags = filter_tags or []
    filter_tags = list(map(str.lower, filter_tags))
    cards = {}

    filepath = _resolve_rel_paths(filepath, base_path=base_path)
    if isinstance(filepath, list) or filepath.is_dir():
        card_paths = _get_cardpath_list(filepath, valid_ext=VALID_EXT, recursive=recursive)
        for p in card_paths:
            project_card = _read_card(
                p, filter_tags=filter_tags, existing_projects=existing_projects
            )
            if project_card is None:
                continue
            if project_card.project in cards:
                msg = f"Project names not unique from projects being read in together in `read_cards()`: {project_card.project}"
                raise ProjectCardReadError(msg)
            cards[project_card.project] = project_card
    else:
        project_card = _read_card(
            filepath, filter_tags=filter_tags, existing_projects=existing_projects
        )
        if project_card is not None:
            cards[project_card.project] = project_card
    if len(cards) == 0:
        CardLogger.warning("No project cards found with given parameters.")
    return cards


def _resolve_rel_paths(
    filepath: ProjectCardFilepaths, base_path: Path = DEFAULT_BASE_PATH
) -> Union[Path, list[Path]]:
    """Resolves relative paths to absolute paths.

    Args:
        filepath: path or list of paths to resolve.
        base_path: base path to resolve relative paths from.
    """
    base_path = Path(base_path).resolve()

    def resolve_single_path(p: Union[Path, str]) -> Path:
        p = Path(p)
        if p.is_absolute():
            return p
        return (base_path / p).resolve()

    if isinstance(filepath, list):
        return [resolve_single_path(p) for p in filepath]
    return resolve_single_path(filepath)
