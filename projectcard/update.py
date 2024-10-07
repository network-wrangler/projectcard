"""Updates older project cards to current format.

Contains three public functions:

1. `update_schema_for_card`: Updates a card to the current format.
2. `update_schema_for_card_file`: Updates a card file to the current format.
3. `update_schema_for_card_dir`: Updates all card files in a directory to the current format.

There is a wrapper script for the third function in `/bin/batch_update_project_cards.py`.

Note that this script is tested (`test_conversion_script.py`) to successfully convert all the
project cards in `tests/data/cards/*.v0.yaml` to the current format.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Optional

import yaml

from projectcard import CardLogger, ProjectCard, write_card
from projectcard.io import SKIP_READ
from projectcard.utils import _update_dict_key


def _get_card_files(card_search_dir_or_filename: Path) -> list[Path]:
    if card_search_dir_or_filename.is_dir():
        # Read all .yaml or .yml files in the directory
        card_files = list(Path(card_search_dir_or_filename).rglob("*.[yY]*[mM][lL]*"))
        if not card_files:
            CardLogger.error(f"No card files found in {card_search_dir_or_filename}")
            sys.exit(1)
        return [Path(file) for file in card_files]
    return [Path(card_search_dir_or_filename)]


CATEGORY_NAME_MAP = {
    "Roadway Property Change": "roadway_property_change",
    "Add New Roadway": "roadway_addition",
    "Parallel Managed lanes": "roadway_managed_lanes",
    "Roadway Deletion": "roadway_deletion",
    "Transit Property Change": "transit_property_change",
    "Transit Service Property Change": "transit_property_change",
}

NESTED_VALUES = ["facility", "properties", "property_changes", "links", "nodes"]


def _nest_change_under_category_type(card: dict) -> dict:
    """Nest the change object under category_name.

    Also updates category names based on CATEGORY_NAME_MAP

    eg:

    INPUT:

    ```yaml
    category: category_name
    facility: ...
    ...
    ```

    OUTPUT:

    ```yaml
    category_name:
        facility: ...
        ...
    ```

    """
    # CardLogger.debug(f"Card.nest_change_under_category_type:\n {card}")
    if "changes" in card:
        _updated_changes = []
        for change in card["changes"]:
            # CardLogger.debug(f"...Change: {change}")
            _updated_changes.append(_nest_change_under_category_type(change))
        card["changes"] = _updated_changes
        return card
    if "category" in card:
        category = card.pop("category")

        # CardLogger.debug(f"Category: {category}")
        if category not in CATEGORY_NAME_MAP:
            msg = f"Invalid category: {category}"
            raise ValueError(msg)
        category_key = CATEGORY_NAME_MAP[category]
        card[category_key] = {k: card.pop(k) for k in NESTED_VALUES if k in card}
        # CardLogger.debug(f"Updated Card.nest_change_under_category_type:\n {card}")
        return card

    CardLogger.info(f"Can't find category in: {card}. This card might already be updated?")
    return card


DEFAULT_ROADWAY_VALUES: dict = {
    "links": {
        "name": "new_link - TODO NAME ME!",
        "roadway": "road",
        "bus_only": 0,
        "rail_only": 0,
        "drive_access": 1,
        "bike_access": 1,
        "walk_access": 1,
    },
    "nodes": {},
}

REPLACE_ROADWAY_VALUES = {
    "roadway": {
        "ramp": "motorway_link",
        "Ramp": "motorway_link",
        "Trunk": "trunk",
    }
}


def _drop_empty_object(card: dict) -> dict:
    """Dependencies, notes and tags should be dropped if empty string or None."""
    for key in ["dependencies", "tags", "notes"]:
        if key in card and (card[key] == "" or card[key] is None):
            card.pop(key)
    return card


def _tags_to_list(card: dict) -> dict:
    """Convert tags to list if not already."""
    if "tags" in card and isinstance(card["tags"], str):
        card["tags"] = [card["tags"]]
    return card


def _update_roadway_addition(change, default_roadway_values: dict = DEFAULT_ROADWAY_VALUES):
    """Adds required link and node values for roadway additions with assumed defaults.

    Also updates roadway names to lowercase and changes "ramp" to "motorway_link".

    Args:
        change: ProjectCard dictionary to update.
        default_roadway_values (dict): Mapping of field name and default value to use for links if
            not specified in project card. Defaults to DEFAULT_ROADWAY_VALUES.
    """
    if "roadway_addition" not in change:
        return change
    network_parts = ["links", "nodes"]
    for p in network_parts:
        if p not in change["roadway_addition"]:
            continue
        for item in change["roadway_addition"][p]:
            for field, default_value in default_roadway_values[p].items():
                if field not in item or item[field] is None or item[field] == "":
                    item[field] = default_value
                if field in [
                    "walk_access",
                    "bike_access",
                    "drive_access",
                    "bus_only",
                    "rail_only",
                ]:
                    item[field] = int(item[field])
            if p == "links":
                item["roadway"] = item["roadway"].lower()
                if "ramp" in item["roadway"]:
                    item["roadway"] = "motorway_link"
    CardLogger.debug(f"Updated Card.update_roadway_addition:\n {change}")
    return change


def _unnest_scoped_properties(property_change: dict) -> dict:
    """Update keys scoped managed lanes to a list of single-level dicts"".

    e.g.

    from:

    ```yaml
    timeofday:
     - timespan: [08:00,11:00]
       value: abc
     - timespan: 12:00,14:00]
       value: xyz
    ```

    to:

    ```yaml
    scoped:
     - timespan: [08:00,11:00]
       value: abc
     - timespan: 12:00,14:00]
       value: xyz
    ```

    And from:

    ```yaml
    group:
     - category: A
        - timespan: [08:00,11:00]
           value: 1
        - timespan: [14:00,16:00]
           value: 11
     - category: B
       - timespan: [08:00,11:00]
           value: 2
        - timespan: [14:00,16:00]
           value: 22
    ```

    TO:

    ```yaml
    scoped:
    - category: A
      timespan: [08:00,11:00]
      value: 1
    - category:A
      timespan: [14:00,16:00]
      value: 11
    - category: B
      timespan: [08:00,11:00]
      value: 2
    - category: B
      timespan: .[14:00,16:00]
      value: 22
    ```
    """
    if "group" in property_change:
        property_change["scoped"] = []
        for cat, change_list in property_change["group"].items():
            for change in change_list:
                property_change["scoped"].append(change.update({"category": cat}))
        property_change.pop("group")

    elif "timeofday" in property_change:
        property_change["scoped"] = []
        for change in property_change["timeofday"]:
            property_change["scoped"].append(change)
        property_change.pop("timeofday")
    return property_change


def _update_property_changes_key(change: dict) -> dict:
    """Update "properties" to "property_changes" and nest under the property name.

    e.g.

    FROM:

    ```yaml
    properties:
    - property: trn_priority
        set: 2
    ```

    TO:

    ```yaml
    property_changes:
        trn_priority:
            set: 2
    ```

    """
    if "roadway_property_change" in change:
        change_name = "roadway_property_change"
    elif "transit_property_change" in change:
        change_name = "transit_property_change"
    else:
        return change

    if "properties" not in change[change_name]:
        return change

    CardLogger.debug(f"Card.update_property_changes_key:\n {change}")
    _pchanges = change[change_name].pop("properties")
    updated_pchanges = {}
    for _pc in _pchanges:
        _updated_pc = copy.deepcopy(_pc)
        property_name = _updated_pc.pop("property")
        if "group" in _pc or "timeofday" in _pc:
            _updated_pc = _unnest_scoped_properties(_updated_pc)
        updated_pchanges[property_name] = _updated_pc
    change[change_name]["property_changes"] = updated_pchanges
    CardLogger.debug(f"Updated Card.update_property_changes_key:\n {change}")
    return change


ROADWAY_FACILITY_UPDATED_KEYS = {"link": "links", "A": "from", "B": "to"}


def _update_roadway_facility(change: dict) -> dict:
    """Update keys for "facility" dict under "roadway_property_change".

    Also unnests "links" from an unnecessary list.

    Makes changes specified in ROADWAY_FACILITY_UPDATED_KEYS:
        link to "links"
        A to "from"
        B to "to"
    """
    if "roadway_property_change" not in change:
        return change

    facility = change["roadway_property_change"].pop("facility")

    # update prop names
    for old_key, new_key in ROADWAY_FACILITY_UPDATED_KEYS.items():
        if old_key in facility:
            facility[new_key] = facility.pop(old_key)

    # unnest links from list
    if "links" in facility:
        if facility["links"] == "all":
            facility["links"] = {"all": "True"}
        else:
            facility["links"] = facility.pop("links")[0]

    change["roadway_property_change"]["facility"] = facility
    CardLogger.debug(f"Updated Card.update_roadway_facility:\n {change}")
    return change


def _update_transit_service(change):
    """For a change with "transit" in the title, update 'facility' to 'service' and change format.

    Nest under trip_properties and route_properties as follows:

    trip_properties: trip_id, route_id, direction_id
    route_properties: route_long_name, route_short_name, agency_id

    Update "time" value to be a list of lists under property "timespans".

    e.g.

    FROM:

    ```yaml
    transit_property_change:
        facility:
            trip_id: ['123']
            route_id: [21-111, 53-111]
            time:  ['09:00', '15:00']
            route_long_name:['express']
            route_short_name:['exp']
            agency_id: ['1']
            direction_id: 0
    ```

    TO:

    ```yaml
    transit_property_change:
        service:
            trip_properties:
                trip_id: ['123']
                route_id: ['21-111,' '53-111']
                direction_id: 0
            timespans: [['09:00', '15:00']]
            route_properties:
                route_long_name: ['express']
                route_short_name: ['exp']
                agency_id: ['1']
    ```

    """
    if "facility" not in change.get("transit_property_change", {}):
        _tpc = change.get("transit_property_change", {})
        CardLogger.debug(f"card.get(...): { _tpc}")
        return change

    ROUTE_PROPS = ["route_long_name", "route_short_name", "agency_id"]
    TRIP_PROPS = ["trip_id", "route_id", "direction_id"]
    NOT_A_LIST = ["direction_id"]
    facility = change["transit_property_change"].pop("facility")
    trip_properties = {}
    route_properties = {}
    timespans = []

    for key, value in facility.items():
        v = [value] if value is not list and key not in NOT_A_LIST else value
        if key in TRIP_PROPS:
            trip_properties[key] = v
        elif key in ROUTE_PROPS:
            route_properties[key] = v
        elif key == "timespan":
            # timespans is a list of a list
            timespans = v
        else:
            msg = f"Unimplemented transit property: {key}"
            raise NotImplementedError(msg)
    change["transit_property_change"]["service"] = {}
    if trip_properties:
        change["transit_property_change"]["service"]["trip_properties"] = trip_properties
    if route_properties:
        change["transit_property_change"]["service"]["route_properties"] = route_properties
    if timespans:
        change["transit_property_change"]["service"]["timespans"] = timespans

    CardLogger.debug(f"Updated Card.Updated Transit Service:\n {change}")
    return change


def _update_transit_routing(change):
    if (
        "transit_property_change" in change
        and "routing" in change["transit_property_change"]["property_changes"]
    ):
        transit_property_change = change.pop("transit_property_change")

        change["transit_routing_change"] = {
            "service": transit_property_change["service"],
            "routing": transit_property_change["property_changes"]["routing"],
        }
    return change


def _update_change(change_data: dict) -> dict:
    """Update change object in card data to current format."""
    change_data = _update_property_changes_key(change_data)
    change_data = _update_roadway_addition(change_data)
    change_data = _update_roadway_facility(change_data)
    change_data = _update_transit_service(change_data)
    change_data = _update_transit_routing(change_data)
    return change_data


def _remove_empty_strings(data):
    """Remove keys/values with empty string values from dictionaries and lists."""
    if isinstance(data, dict):
        return {k: _remove_empty_strings(v) for k, v in data.items() if v != ""}
    if isinstance(data, list):
        return [_remove_empty_strings(item) for item in data if item != ""]
    return data


def _literals_to_arrays(data):
    """Make tags arrays even if just one."""
    if isinstance(data.get("tags", []), str):
        data["tags"] = [data["tags"]]
    return data


def _clean_floats_to_ints(data):
    """Convert floats to ints if they are whole numbers."""
    if isinstance(data, dict):
        return {k: _clean_floats_to_ints(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_clean_floats_to_ints(item) for item in data]
    if isinstance(data, float) and data.is_integer():
        return int(data)
    try:
        data = float(data)
        if data.is_integer():
            return int(data)
        return data
    except:
        return data


def update_schema_for_card(card_data: dict) -> dict:
    """Update older project card data in dictionary to current format.

    Example usage:

    ```python
    new_card_data = update_schema_for_card(old_card_data_dict)
    write_card(new_card_data, Path("my_new_card.yml"))
    ```

    Args:
        card_data: card data to update.
        errlog_output_dir: directory to log erroneous data for further examination. Defaults to ".".
    """
    _project = card_data["project"]
    CardLogger.info(f"Updating {_project}...")
    card_data = _drop_empty_object(card_data)
    card_data = _tags_to_list(card_data)
    card_data = _nest_change_under_category_type(card_data)
    card_data = _update_dict_key(card_data, "roadway_managed_lanes", "roadway_property_change")
    card_data = _update_dict_key(card_data, "time", "timespan")

    if "changes" in card_data:
        _updated_changes = []
        for change in card_data["changes"]:
            CardLogger.debug(f"...Change: {change}")
            _updated_changes.append(_update_change(change))
        card_data["changes"] = _updated_changes
    else:
        card_data = _update_change(card_data)

    """
    TODO: validate against ProjectCardModel when that is updated before returning

    CardLogger.info(f"...validating against ProjectCardModel")
    try:
        ProjectCardModel(**card_data)
    except Exception as e:
        _outfile_path = errlog_output_dir / (_project + ".ERROR_DUMP.yaml")
        with open(_outfile_path, "w") as outfile:
            yaml.dump(card_data, outfile, default_flow_style=False, sort_keys=False)
        CardLogger.error(f"Erroneous data dumped to { _outfile_path}")
        raise e
    """

    return card_data


def update_schema_for_card_file(
    input_card_path: Path, output_card_path: Optional[Path] = None, rename_input: bool = False
) -> None:
    """Update previous project card files to current format.

    Example usage:

    ```python
    update_schema_for_card_file(Path("my_old_card.yml"), Path("/home/me/newcards/")
    ```

    Args:
        input_card_path: path to card file.
        output_card_path: path to write updated card file. Defaults to None. If None, will
            write to input_card_path with a v1 pre-suffix.
        rename_input: rename input card file with a ".v0 pre-suffix. Default: False
    """
    card_data = yaml.safe_load(input_card_path.read_text())
    for k in SKIP_READ:
        if k in card_data:
            del card_data[k]

    if output_card_path is None:
        output_card_path = input_card_path.parent / (
            input_card_path.stem + ".v1" + input_card_path.suffix
        )

    if output_card_path.is_dir():
        output_card_path = output_card_path / (
            input_card_path.stem + ".v1" + input_card_path.suffix
        )
    if rename_input:
        output_card_path = input_card_path
        input_card_path.rename(
            input_card_path.parent / (input_card_path.stem + ".v0" + input_card_path.suffix)
        )

    card_data = update_schema_for_card(card_data)
    CardLogger.debug("Completed updating schema.\n...initializing as ProjectCard")
    CardLogger.debug(f"card_data:\n{card_data}")
    card = ProjectCard(card_data)
    CardLogger.debug(f"Initialized as ProjectCard.\n...writing to {output_card_path}")
    CardLogger.debug(f"ProjectCard:\n{card}")
    # Write it out first so that it is easier to troubleshoot
    write_card(card, output_card_path)
    CardLogger.debug(f"Completed writing.\n...validating")
    assert card.valid


def update_schema_for_card_dir(
    input_card_dir: Path, output_card_dir: Optional[Path] = None, rename_input: bool = False
) -> None:
    """Update all card files in a directory to current format.

    Example usage:

    ```python
    update_schema_for_card_dir(Path("/home/me/oldcards"), Path("/home/me/newcards/")
    ```

    Args:
        input_card_dir: directory with card files.
        output_card_dir: directory to write updated card files. Defaults to None. If None, will
            write to input_card_dir with a v1 pre-suffix.
        rename_input: rename input card files with a v0 pre-suffix. Default: False
    """
    # check that input and output paths are valid
    if not input_card_dir.exists():
        msg = f"Invalid input_card_dir: {input_card_dir}"
        raise ValueError(msg)

    if output_card_dir is None:
        output_card_dir = input_card_dir.parent / (input_card_dir.name + "_v1")
    elif input_card_dir == output_card_dir:
        msg = "Error: output_dir cannot be the same as card_search_dir."
        raise ValueError(msg)
    output_card_dir.mkdir(parents=True, exist_ok=True)

    if input_card_dir.is_file():
        if output_card_dir is not None and input_card_dir.parent == output_card_dir:
            msg = "Error: output_dir cannot be the same as the directory of card_search_dir."
            raise ValueError(msg)
        input_card_files = [input_card_dir]
    else:
        input_card_files = _get_card_files(input_card_dir)

    for input_card in input_card_files:
        output_subfolder = input_card.relative_to(input_card_dir).parent
        output_card_path = (
            output_card_dir / output_subfolder / (input_card.stem + input_card.suffix)
        )
        output_card_path.parent.mkdir(parents=True, exist_ok=True)
        update_schema_for_card_file(input_card, output_card_path, rename_input)
