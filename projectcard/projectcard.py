#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import json
from glob import glob
from typing import Any, Collection, Mapping
from pathlib import Path

import toml
import yaml

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError

logger = logging.getLogger(__name__)

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTCARD_SCHEMA = os.path.join(ROOTDIR,"schema","projectcard.json")

def read(filepath:str, _cards: Collection = []) -> dict:
    """Reads project cards by inferring the file type.

    Args:
        filepath: where the project card is.  A single path, list of paths,
            a directory, or a glob pattern.

    Returns: collection of Attribute Dictionaries for Project Card
    """
    _method_map = {
        ".yml": _read_yml,
        ".yaml": _read_yml,
        ".json": _read_json,
        ".toml": _read_toml,
        ".wr": _read_wrangler,
        ".wrangler": _read_wrangler,
    }
    if not Path(filepath).is_file():
        _card_paths = _get_cardpath_list(filepath, valid_ext = _method_map.keys())
        for p in _card_paths:
            _cards+=read(p, _cards = _cards)
        return _cards
    _ext = os.path.splitext(filepath)[1]    
    if _ext not in _method_map.keys():
        raise ValueError("Unsupported file type: {}".format(_ext))
    _c = _method_map[_ext](filepath)
    _cards.append(_c)
    return _cards

def _get_cardpath_list(filepath, valid_ext:Collection[str] = []):
    """Returns a list of valid paths to project cards given a search string.

    Args:
        filepath: where the project card is.  A single path, list of paths,
            a directory, or a glob pattern.
        valid_ext: list of valid file extensions

    Returns: list of valid paths to project cards
    """
    logger.debug(f"Getting cardpath list: {filepath} of type {type(filepath)}")
    if isinstance(filepath, list):
        logger.debug(f"Reading list of paths: {filepath}")
        if not all(Path(f).is_file() for f in filepath):
            _missing = [f for f in filepath if not Path(f).is_file()]
            raise FileNotFoundError(f"{_missing} is/are not a file/s")
        _paths = filepath
    elif (isinstance(filepath,Path) or (filepath, str)) and Path(filepath).is_dir():
        logger.debug(f"Getting all files in: {filepath}")
        _paths = [p for p in Path(filepath).glob("*")]
    else:
        raise ValueError(f"filepath: {filepath} not understood.")
    logger.debug(f"All paths: {_paths}")
    _card_paths = [p for p in _paths if p.suffix in valid_ext]
    logger.debug(f"Reading set of paths: {_card_paths}")
    return _card_paths

def _read_yml(filepath: str) -> dict:
    logger.debug(f"Reading YML: {filepath}")
    with open(filepath, "r") as cardfile:
        attribute_dictionary = yaml.safe_load(cardfile)
        attribute_dictionary["file"] = filepath

    return attribute_dictionary

def _read_toml(filepath: str) -> dict:
    logger.debug(f"Reading TOML: {filepath}")
    with open(filepath, "r", encoding="utf-8") as cardfile:
        attribute_dictionary = toml.load(cardfile)
        attribute_dictionary["file"] = filepath

    return attribute_dictionary

def _read_json(filepath: str) -> dict:
    logger.debug(f"Reading JSON: {filepath}")
    with open(filepath, "r") as cardfile:
        attribute_dictionary = json.safe_load(cardfile)
        attribute_dictionary["file"] = filepath

    return attribute_dictionary

def _read_wrangler(filepath: str) -> dict:
    logger.debug(f"Reading Wrangler: {filepath}")
    with open(filepath, "r") as cardfile:
        delim = cardfile.readline()
        _yaml, _pycode = cardfile.read().split(delim)
 
    attribute_dictionary = yaml.safe_load(_yaml)
    attribute_dictionary["file"] = filepath
    attribute_dictionary["pycode"] = _pycode.lstrip("\n")

    return attribute_dictionary


def validate(jsondata, schema=PROJECTCARD_SCHEMA):
    try:
        validate(jsondata, schema)
    except ValidationError as e:
        raise ValidationError(f"{e}")
    except SchemaError as e:
        raise SchemaError(f"{e}")
