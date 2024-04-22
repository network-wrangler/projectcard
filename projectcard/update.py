"""Updates older project cards to current format.

Contains three public functions:

1. `update_schema_for_card`: Updates a card to the current format.
2. `update_schema_for_card_file`: Updates a card file to the current format.
3. `update_schema_for_card_dir`: Updates all card files in a directory to the current format.

There is a wrapper script for the third function in `/bin/batch_update_project_cards.py`.

Note that this script is tested (`test_conversion_script.py`) to successfully convert all the 
project cards in `tests/data/cards/*.v0.yaml` to the current format.  
"""
import sys
from pathlib import Path

import yaml

from projectcard import ProjectCard, write_card
from projectcard.utils import _update_dict_key
from projectcard.models import ProjectCardModel
from projectcard import CardLogger


def _get_card_files(card_search_dir_or_filename: Path) -> list[Path]:
    if card_search_dir_or_filename.is_dir():
        # Read all .yaml or .yml files in the directory
        card_files = list(Path(card_search_dir_or_filename).rglob("*.[yY][aA]?[mM][lL]*"))
        if not card_files:
            print(f"No card files found in {card_search_dir_or_filename}")
            sys.exit(1)
        return [Path(file) for file in card_files]
    else:
        return [Path(card_search_dir_or_filename)]


CATEGORY_NAME_MAP = {
    "Roadway Property Change": "roadway_property_change",
    "Add New Roadway": "roadway_addition",
    "Parallel Managed lanes": "roadway_managed_lanes",
    "Roadway Deletion": "roadway_deletion",
    "Transit Property Change": "transit_property_change",
    "Transit Service Property Change": "transit_property_change",
}

NESTED_VALUES = ['facility', 'properties', 'property_changes', 'links', 'nodes']


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
    CardLogger.debug(f"Card.nest_change_under_category_type:\n {card}")
    if "changes" in card:
        _updated_changes = []
        for change in card["changes"]:
            CardLogger.debug(f"...Change: {change}")
            _updated_changes.append(_nest_change_under_category_type(change))
        card["changes"] = _updated_changes
        return card
    elif "category" in card:
        category = card.pop("category")

        CardLogger.debug(f"Category: {category}")
        if category not in CATEGORY_NAME_MAP:
            raise ValueError(f"Invalid category: {category}")
        category_key = CATEGORY_NAME_MAP[category]
        card[category_key] = {k: card.pop(k) for k in NESTED_VALUES if k in card}
        CardLogger.debug(f"Updated Card.nest_change_under_category_type:\n {card}")
        return card

    else:
        CardLogger.debug(f"Can't find category in: {card}. This card might already be updated?")
        return card


DEFAULT_ROADWAY_VALUES: dict = {
    "links":{
        "name": "new_link - TODO NAME ME!",
        "roadway": "road",
        "bus_only": 0,
        "rail_only": 0,
        "drive_access": 1,
        "bike_access": 1,
        "walk_access": 1,
    },
    "nodes": {
    }
}


def _update_roadway_addition(card, default_roadway_values: dict = DEFAULT_ROADWAY_VALUES):
    """Adds required link and node values for roadway additions with assumed defaults.

    Args:
        card (_type_): _description_
        default_link_values (dict): Mapping of field name and default value to use for links if 
            not specified in project card. Defaults to DEFAULT_ROADWAY_VALUES.

    """
    if "roadway_addition" not in card:
        return card
    network_parts = ["links", "nodes"]
    for p in network_parts:
        if p not in card["roadway_addition"]:
            continue
        for item in card["roadway_addition"][p]:
            for field, default_value in default_roadway_values[p].items():
                if field not in item:
                    item[field] = default_value

    CardLogger.debug(f"Updated Card.update_roadway_addition:\n {card}")
    return card

def _unnest_scoped_properties(property_change:dict)->list[dict]:
    """Update keys scoped managed lanes to a list of single-level dicts""

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
            property_change["scoped"].append(change.update({"category": cat}))
        property_change.pop("category")
        return property_change


def _update_property_changes_key(card):
    """Find "properties" key and update to "property_changes" and to nest as object under the property name .

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
    if "properties" not in card:
        return card
    CardLogger.debug(f"Card.update_property_changes_key:\n {card}")
    _pchanges = card.pop("properties")
    updated_pchanges = {}
    for _pc in _pchanges:
        property_name = _pc.pop("property")
        if "group" in _pc or "timeofday" in _pc:
            _pc = _unnest_scoped_properties(_pc)
        updated_pchanges[property_name] = _pc
    card["property_changes"] = updated_pchanges
    CardLogger.debug(f"Updated Card.update_property_changes_key:\n {card}")
    return card


ROADWAY_FACILITY_UPDATED_KEYS = {"link": "links", "A": "from", "B": "to"}


def _update_roadway_facility(card):
    """Update keys for "facility" dict under "roadway_property_change or roadway_managed_lanes""

    Also unnests "links" from an unnecessary list.

    Makes changes specified in ROADWAY_FACILITY_UPDATED_KEYS:
        link to "links"
        A to "from"
        B to "to"
    """
    applicable_categories = ["roadway_property_change", "roadway_managed_lanes"]
    for change_cat in applicable_categories:
        if change_cat not in card:
            continue

        for old_key, new_key in ROADWAY_FACILITY_UPDATED_KEYS.items():
            if old_key in card[change_cat]["facility"]:
                card[change_cat]["facility"][new_key] = card[
                    change_cat
                ]["facility"].pop(old_key)

        # unnest links from list
        if "links" in card[change_cat]["facility"]:
            card[change_cat]["facility"]["links"] = card[change_cat][
                "facility"
            ].pop("links")[0]
        CardLogger.debug(f"Updated Card.update_roadway_facility:\n {card}")
    return card


def _update_transit_service(card):
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
    if "facility" not in card.get("transit_property_change", {}):
        _tpc = card.get("transit_property_change", {})
        CardLogger.debug(f"card.get(...): { _tpc}")
        return card

    ROUTE_PROPS = ["route_long_name", "route_short_name", "agency_id"]
    TRIP_PROPS = ["trip_id", "route_id", "direction_id"]
    NOT_A_LIST = ["direction_id"]
    facility = card["transit_property_change"].pop("facility")
    trip_properties = {}
    route_properties = {}
    timespans = []

    for key, value in facility.items():
        if value is not list and key not in NOT_A_LIST:
            value = [value]
        if key in TRIP_PROPS:
            trip_properties[key] = value
        elif key in ROUTE_PROPS:
            route_properties[key] = value
        elif key == "time":
            # timespans is a list of a list
            timespans = value
        else:
            raise ValueError(f"Unimplemented transit property: {key}")
    card["transit_property_change"]["service"] = {}
    if trip_properties:
        card["transit_property_change"]["service"]["trip_properties"] = trip_properties
    if route_properties:
        card["transit_property_change"]["service"]["route_properties"] = route_properties
    if timespans:
        card["transit_property_change"]["service"]["timespans"] = timespans

    CardLogger.debug(f"Updated Card.Updated Transit Service:\n {card}")
    return card


def _update_transit_routing(card):
    """
    """
    if "transit_property_change" in card:
         # TODO do "shapes"
        if "routing" in card["transit_property_change"]["property_changes"]:
            transit_property_change = card.pop("transit_property_change")

            card["transit_routing_change"] = {
                "service": transit_property_change["service"],
                "routing": transit_property_change["property_changes"]["routing"]
            }
    return card


def _update_timespan(card):
    """Find "time" key and update to "timespan" in a nested dictionary.

    Args:
        card: The card dictionary to update.

    Returns:
        The updated card dictionary.
    """
    card = _update_dict_key(card, "time", "timespan")

    CardLogger.debug(f"Updated Card.update_timespan:\n {card}")
    return card


def update_schema_for_card(card_data: dict, errlog_output_dir: Path = ".") -> dict:
    """Update older project card data in dictionary to current format.

    Example usage:

    ```python
    new_card_data = update_schema_for_card(old_card_data_dict)
    write_card(new_card_data, Path("my_new_card.yml"))
    ```

    args:
        card_data: card data to update.
        errlog_output_dir: directory to log erroneous data for further examination. Defaults to ".".
    """
    _project = card_data['project']
    CardLogger.info(f"Updating {_project}...")
    card_data = _update_property_changes_key(card_data)
    card_data = _nest_change_under_category_type(card_data)
    card_data = _update_roadway_addition(card_data)
    card_data = _update_roadway_facility(card_data)
    card_data = _update_transit_service(card_data)
    card_data = _update_transit_routing(card_data)
    card_data = _update_timespan(card_data)
   
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
    input_card_path: Path, output_card_path: Path = None, rename_input: bool = False
) -> None:
    """Update previous project card files to current format.

    Example usage:

    ```python
    update_schema_for_card_file(Path("my_old_card.yml"), Path("/home/me/newcards/")
    ```

    args:
        input_card_path: path to card file.
        output_card_path: path to write updated card file. Defaults to None. If None, will
            write to input_card_path with a v1 pre-suffix.
        rename_input: rename input card file with a ".v0 pre-suffix. Default: False
    """

    card_data = yaml.safe_load(input_card_path.read_text())

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

    card_data = update_schema_for_card(card_data, errlog_output_dir=output_card_path.parent)
    card = ProjectCard(card_data)
    # Write it out first so that it is easier to troubleshoot
    write_card(card, output_card_path)
    assert card.valid


def update_schema_for_card_dir(
    input_card_dir: Path, output_card_dir: Path = None, rename_input: bool = False
) -> None:
    """Update all card files in a directory to current format.


    Example usage:

    ```python
    update_schema_for_card_dir(Path("/home/me/oldcards"), Path("/home/me/newcards/")
    ```

    args:
        input_card_dir: directory with card files.
        output_card_dir: directory to write updated card files. Defaults to None. If None, will
            write to input_card_dir with a v1 pre-suffix.
        rename_input: rename input card files with a v0 pre-suffix. Default: False
    """

    # check that input and output paths are valid
    if not input_card_dir.exists():
        raise ValueError(f"Invalid input_card_dir: {input_card_dir}")

    if output_card_dir is not None:
        if not output_card_dir.exists():
            raise ValueError(f"Invalid output_dir: {output_card_dir}")

        if input_card_dir == output_card_dir:
            raise ValueError(
                "Error: output_dir cannot be the same as card_search_dir or card_filename."
            )

    if input_card_dir.is_file():
        if output_card_dir is not None and input_card_dir.parent == output_card_dir:
            raise ValueError(
                "Error: output_dir cannot be the same as the directory of card_search_dir or card_filename."
            )
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
