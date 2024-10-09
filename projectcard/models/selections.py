"""Data models for selecting nodes, links, and trips in a project card."""

from typing import Annotated, ClassVar, Optional

from pydantic import BaseModel, ConfigDict, Field

from .fields import Mode, Timespan
from .structs import (
    SelectRoadNode,
    SelectRouteProperties,
    SelectTransitLinks,
    SelectTransitNodes,
    SelectTripProperties,
)


class SelectRoadNodes(BaseModel):
    """Requirements for describing multiple nodes of a project card (e.g. to delete).

    Attributes:
        all (bool): If True, select all nodes. Must have either `all`, `osm_node_id` or
            `model_node_id`.
        osm_node_id (Optional[list[str]]): List of OSM node IDs to select. Must have either
            `all`, `osm_node_id` or `model_node_id`.
        model_node_id (Optional[list[int]]): List of model node IDs to select. Must have either
            `all`, `osm_node_id` or `model_node_id`.
        ignore_missing (bool): If True, ignore missing nodes. Otherwise, raise an error
            if they are not found. Defaults to True.

    !!! Example "Example Roadway Nodes"
        ```yaml
        nodes:
            model_node_id: [12345, 67890]
        ```
    """

    require_any_of: ClassVar = [["osm_node_id", "model_node_id"]]
    model_config = ConfigDict(extra="forbid", coerce_numbers_to_str=True)

    all: Optional[bool] = False
    osm_node_id: Annotated[Optional[list[str]], Field(None, min_length=1)]
    model_node_id: Annotated[Optional[list[int]], Field(min_length=1)]
    ignore_missing: Optional[bool] = True


class SelectRoadLinks(BaseModel):
    """Requirements for describing links in the `facility` section of a project card.

    Must have one of `all`, `name`, `osm_link_id`, or `model_link_id`.
    Additional fields to select on may be provided and will be treated as an AND condition after
        the primary selection from `all`, `name`, `osm_link_id`, or `model_link_id`.

    Attributes:
        all (bool): If True, select all links.
        name (Optional[list[str]]): List of names to select. If multiple provided will
            be treated as an OR condition.
        ref (Optional[list[str]]): Open Street Map `ref` which usually refers to a route
            or exit number.  See: <https://wiki.openstreetmap.org/wiki/Key:ref>. If multiple
            provided will be treated as an OR condition.
        osm_link_id (Optional[list[str]]): List of OSM link IDs to select. If multiple provided
            will be treated as an OR condition.
        model_link_id (Optional[list[int]]): List of model link IDs to select. If multiple provided
            will be treated as an OR condition.
        modes (Optional[Modes]): List of modes to select. If multiple provided will be
            treated as an OR condition.
        ignore_missing (bool): If True, ignore missing links. Otherwise, raise an error
            if they are not found. Defaults to True.

    !!! Example "Example: 2 and 3 lane drivable links named 'Main St' or 'Broadway'."
        ```yaml
        links:
            name: ["Main St", "Broadway"]
            modes: ["drive"]
            lanes: [2, 3]
        ```

    !!! Example "Example: Links with model_link_id 12345 or 67890."
        ```yaml
        links:
            model_link_id: [12345, 67890]
        ```

    !!! Example "Example: Links where biking is allowed but driving is not."
        ```yaml
        links:
            all: True
            bike_allowed: true
            drive_allowed: false
        ```
    """

    require_conflicts: ClassVar = [
        ["all", "osm_link_id"],
        ["all", "model_link_id"],
        ["all", "name"],
        ["all", "ref"],
        ["osm_link_id", "model_link_id"],
        ["osm_link_id", "name"],
        ["model_link_id", "name"],
    ]
    require_any_of: ClassVar = [["name", "ref", "osm_link_id", "model_link_id", "all"]]

    model_config = ConfigDict(extra="allow", coerce_numbers_to_str=True)

    all: Optional[bool] = False
    name: Annotated[Optional[list[str]], Field(None, min_length=1)]
    ref: Annotated[Optional[list[str]], Field(None, min_length=1)]
    osm_link_id: Annotated[Optional[list[str]], Field(None, min_length=1)]
    model_link_id: Annotated[Optional[list[int]], Field(None, min_length=1)]
    modes: Annotated[Optional[list[Mode]], Field(None, min_length=1)]
    ignore_missing: Optional[bool] = True

    _examples: ClassVar[list[dict]] = [
        {"name": ["Main St"], "modes": ["drive"]},
        {"osm_link_id": ["123456789"]},
        {"model_link_id": [123456789], "modes": ["walk"]},
        {"all": "True", "modes": ["transit"]},
    ]


class SelectTransitTrips(BaseModel):
    """Selection of transit trips.

    Each selection must have at least one of `trip_properties`, `route_properties`, `nodes`,
    or `links`.

    Multiple requirements are treated as an AND condition.

    Attributes:
        trip_properties (Optional[SelectTripProperties]): Selection based on trip properties.
        route_properties (Optional[SelectRouteProperties]): Selection based on route properties.
        timespans (List[Timespan]): List of timespans to select. Multiple timespans are treated
            as an OR condition.
        nodes (Optional[SelectTransitNodes]): Transit nodes to select. Useful for querying
            stops that might be moved/deleted when a roadway is changed.
        links (Optional[SelectTransitLinks]): Selection of transit links. Useful for querying
            links that might be moved/deleted when a roadway is changed.

    !!! Example "Example: Select trips on route 1 or 2 that run between 12:00 and 19:45."
        ```yaml
        service:
            route_properties:
                route_id: ["1", "2"]
            timespans:
                - ["12:00", "19:45"]
        ```

    !!! Example "Example: Select express route trips that goes through nodes 1, 2, and 3."
        ```yaml
        service:
            route_properties:
                route_short_name: ["EXP*"]
            nodes:
                stop_id: [1, 2, 3]
                require: "all"
        ```
    """

    trip_properties: Annotated[Optional[SelectTripProperties], Field(None)]
    route_properties: Annotated[Optional[SelectRouteProperties], Field(None)]
    timespans: Annotated[Optional[list[Timespan]], Field(None, min_length=1)]
    nodes: Annotated[Optional[SelectTransitNodes], Field(None)]
    links: Annotated[Optional[SelectTransitLinks], Field(None)]

    model_config = ConfigDict(
        extra="forbid",
        protected_namespaces=(),
    )


class SelectFacility(BaseModel):
    """Roadway Facility Selection.

    Each selection must have at either: `links`, `nodes`, or `links` and `from` and `to`.

    Specifying `links`, `from`, and `to` will attempt to select a continuous path between the
        two nodes which as much as possible follows the initial link selection that is provided
        (e.g. `name`, `osm_link_id`, `model_link_id`, `ref`) using the specified `modes`.
        Secondary selection parameters (e.g. `lanes`, `price`) will be used to filter the
        continuous path - reulting in a final selection of links that may or may not connect
        the two nodes.

    Attributes:
        links (Optional[SelectRoadLinks]): Selection of roadway links.
        nodes (Optional[SelectRoadNodes]): Selection of roadway nodes.
        from (Optional[SelectRoadNode]): Selection of the origin node.
        to (Optional[SelectRoadNode]): Selection of the destination node.

    !!! Example "Example: Select all links between osm nodes 1 and 2 along `main`."
        ```yaml
        facility:
            links:
                name: ["main"]
            from:
                osm_node_id: "1"
            to:
                osm_node_id: "2"
        ```

    !!! Example "Example: Select links between model nodes 4 and 5 along I-95 that are 3 lanes."
        ```yaml
        facility:
            links:
                ref: ["I-95"]
                lanes: [3]
            from:
                model_node_id: 4
            to:
                model_node_id: 5
        ```

    !!! Example "Example: Select all links on SR320 which have 1 or 2 managed lanes."
        ```yaml
        facility:
            links:
                ref: ["SR320"]
                ML_lanes: [1, 2]
        ```
    """

    require_one_of: ClassVar = [
        ["links", "nodes", ["links", "from", "to"]],
    ]
    model_config = ConfigDict(extra="forbid")

    links: Optional[SelectRoadLinks] = None
    nodes: Optional[SelectRoadNodes] = None
    from_: Annotated[Optional[SelectRoadNode], Field(None, alias="from")]
    to: Optional[SelectRoadNode] = None
