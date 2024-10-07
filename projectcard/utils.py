"""Utility functions for projectcard."""


def _findkeys(node, kv):
    """Returns values of all keys in various objects.

    Adapted from arainchi on Stack Overflow:
    https://stackoverflow.com/questions/9807634/find-all-occurrences-of-a-key-in-nested-dictionaries-and-lists

    """
    if isinstance(node, list):
        for i in node:
            for x in _findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in _findkeys(j, kv):
                yield x


def _update_dict_key(dictdata: dict, findkey, replacekey):
    """Update a dictionary key.

    Args:
        dictdata: dictionary to update
        findkey: key to find
        replacekey: key to replace

    Returns:
        dict: updated dictionary

    """
    keys = list(dictdata.keys())  # Create a copy of the dictionary keys
    for key in keys:
        value = dictdata[key]
        if key == findkey:
            dictdata[replacekey] = value
            del dictdata[key]
        if isinstance(value, dict):
            _update_dict_key(value, findkey, replacekey)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _update_dict_key(item, findkey, replacekey)
    return dictdata


def make_slug(text, delimiter: str = "_"):
    """Makes a slug from text."""
    import re

    text = re.sub("[,.;@#?!&$']+", "", text.lower())
    return re.sub("[\ ]+", delimiter, text)


def slug_to_str(slug: str) -> str:
    """Convert a slug to a more readible sstring."""
    return slug.replace("-", " ").replace("_", " ").title()
