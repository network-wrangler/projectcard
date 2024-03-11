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


def _dict_key_loc_value(dictdata: dict, findkey) -> list[tuple]:
    """returns the location and value of each key in a dictionary.

    ex:
        dictdata = {
        "A": {
            "B": {
                "C": "D"
            }
        },
        "E": {
            "C": "G"
        }

        }
        findkey = "C"
        ==> returns (["A", "B", "C"], "D"), (["E", "C"], "G")

    Args:
        dictdata: dictionary to search
        findkey: key to find

    Returns:
        list: tuples of each location of key in dictionary, and its value of key in dictionary
    """

    def _find_key_loc_value(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == findkey:
                    yield (path + [key], value)
                if isinstance(value, dict):
                    yield from _find_key_loc_value(value, path + [key])
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            yield from _find_key_loc_value(item, path + [key, i])

    return list(_find_key_loc_value(dictdata, []))


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
