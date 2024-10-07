"""Structures (lists and objects) used in project card models."""

from typing import Annotated, Any, ClassVar, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..logger import CardLogger
from .fields import Latitude, Longitude, MLAccessEgress, OsmRoadwayType, PositiveInt, Timespan


class Dependencies(BaseModel):
    """Dependencies for a project card."""

    model_config = ConfigDict(extra="forbid")
    conflicts: Optional[list[str]]
    prerequisites: Optional[list[str]]
    corequisites: Optional[list[str]]
    _examples: ClassVar[list[dict]] = [
        {"conflicts": ["a", "b"], "prerequisites": ["c", "d"], "corequisites": ["e", "f"]},
    ]


class TransitABNodes(BaseModel):
    """Single transit link model."""

    A: Optional[int] = None  # model_node_id
    B: Optional[int] = None  # model_node_id

    model_config = ConfigDict(
        extra="forbid",
    )


class IndivScopedPropertySetItem(BaseModel):
    """Value for setting property value for a single time of day and category.

    Must have at least one of `set` or `change`.

    Attributes:
        category: Optional[Union[str, int]]: Category for the property change. If not provided,
            the change will be applied to all categories minus any other categories that are
            provided.
        timespan: Optional[Timespan]: Timespan for the property change. If not provided, the
            change will be applied to the entire timespan minus any other timespans that are
            provided.
        set: Optional[Any]: Value to set for the property change.
        existing: Optional[Any]: Existing value for the property change.
        change: Optional[Union[int, float]]: Change value for the property change.

    !!! Example "Example Scoped Property Set"
        ```yaml
        scoped:
        - category: hov3
          timespan: ['6:00', '9:00']
          set: 2.0
        - category: hov2
          change: 1
        ```
    """

    model_config = ConfigDict(extra="forbid", exclude_none=True)

    category: Optional[Union[str, int]]
    timespan: Optional[Timespan]
    set: Optional[Any] = None
    existing: Optional[Any] = None
    change: Optional[Union[int, float]] = None


ScopedPropertySetList = list[IndivScopedPropertySetItem]


class TransitPropertyChange_PropertyChanges(BaseModel):
    """Value for setting a single property value for transit."""

    model_config = ConfigDict(extra="forbid", exclude_none=True)

    existing: Optional[Any] = None
    change: Optional[Union[int, float]] = None
    set: Optional[Any] = None
    existing_value_conflict: Optional[Literal["error", "warn", "skip"]] = None

    require_one_of: ClassVar = [
        ["change", "set"],
    ]


class RoadwayPropertyChange(BaseModel):
    """Value for setting a single property value.

    Must have at least one of `set` or `change`.

    Attributes:
        existing: Optional[Any]: Existing value for the property change. Assumption about the
            existing (default, not scoped) value for this property.
        change: Optional[Union[int, float]]: Change value for the property change.  If `scoped` is
            provided, this value will be used as the default value when no scoped value matches.
            Should not be provided if `set` is provided. This value is assumed to be a scalar
            difference to be applied to the existing value.
        set: Optional[Any]: Value to set the property to. If `scoped` is provided, this value
            will be used as the default value when no scoped value matches. Should not be provided
            if `change` is provided.
        scoped: Optional[Union[None, ScopedPropertySetList]]: List of values for the property for
            various `category` (e.g. HOV, truck, etc.) and `timespan` (e.g. 6:00-9:00, 9:00-15:00)
            combinations. When provided, the `set` (or applied `change`) value will be used as
            the default value when no scoped value matches.
        overwrite_scoped: Optional[Literal["conflicting", "all", "error"]]: How to handle
            conflicting scoped property sets. If `conflicting`, conflicting scoped property sets
            will be overwritten. If `all`, all existing scoped property sets will be
            overwritten. If `error`, conflicting scoped property sets will raise an error.
        existing_value_conflict: Optional[Literal["error", "warn", "skip"]]: How to handle
            conflicting existing values. If `error`, conflicting existing values will raise an
            error. If `warn`, conflicting existing values will raise a warning. If `skip`,
            property change will be skipped.

    !!! Example "Example: Reduce lanes by 1...but only if the existing value is 3."
        ```yaml
        lanes:
            existing: 3
            change: -1
            existing_value_conflict: skip
        ```

    !!! Example "Example: Set Peak Hour tolls for HOV3 and HOV2."
        ```yaml
        price:
            overwrite_scoped: all
            change: 0
            scoped:
            - category: hov3
              timespan: ['6:00', '9:00']
              set: 2.0
            - category: hov2
              timespan: ['6:00', '9:00']
              set: 3.0
        ```
    """

    model_config = ConfigDict(extra="forbid", exclude_none=True)

    existing: Optional[Any] = None
    change: Optional[Union[int, float]] = None
    set: Optional[Any] = None
    scoped: Optional[Union[None, ScopedPropertySetList]] = None
    overwrite_scoped: Optional[Literal["conflicting", "all", "error"]] = None
    existing_value_conflict: Optional[Literal["error", "warn", "skip"]] = None

    require_one_of: ClassVar = [
        ["change", "set"],
    ]


class SelectRouteProperties(BaseModel):
    """Selection proeprties for transit routes.

    Assumed to be an AND condition if more than one property is provided.

    Additional properties may be used if they are defined in the transit route table.

    Attributes:
        route_short_name: Optional[List[str]: List of Route short names to select. If more than one
            is provided, the selection will be based on an OR condition. Can also select based on
            a partial match using the '*' wildcard character.
        route_long_name: Optional[List[str]: List of Route long names to select. If more than one
            is provided, the selection will be based on an OR condition. Can also select based on
            a partial match using the '*' wildcard character.
        agency_id: Optional[List[str]: List of Agency IDs to select. If more than one is provided,
            the selection will be based on an OR condition. Can also select based on a partial match
            using the '*' wildcard character.
        route_type: Optional[List[int]: List of Route types to select. If more than one is provided,
            the selection will be based on an OR condition. Can also select based on a partial match
            using the '*' wildcard character.
    """

    model_config = ConfigDict(extra="allow", coerce_numbers_to_str=True)
    route_short_name: Annotated[Optional[list[str]], Field(None, min_length=1)]
    route_long_name: Annotated[Optional[list[str]], Field(None, min_length=1)]
    agency_id: Annotated[Optional[list[str]], Field(None, min_length=1)]
    route_type: Annotated[Optional[list[int]], Field(None, min_length=1)]

    class ConfigDict:
        """Config for the model."""

        protected_namespaces = ()


class SelectTripProperties(BaseModel):
    """Selection properties for transit trips.

    Assumed to be an AND condition if more than one property is provided.

    Additional properties may be used if they are defined in the transit trip table.

    Attributes:
        trip_id: Optional[List[str]: List of Trip IDs to select. If more than one is provided,
            the selection will be based on an OR condition. Can also select based on
            a partial match using the '*' wildcard character.
        shape_id: Optional[List[str]: List of Shape IDs to select. If more than one is
            provided, the selection will be based on an OR condition. Can also select based on
            a partial match using the '*' wildcard character.
        direction_id: Optional[Literal[0, 1]]: Direction ID to select.
        service_id: Optional[List[str]: List Service IDs to select. If more than one is
            provided, the selection will be based on an OR condition. Can also select based on
            a partial match using the '*' wildcard character.
        route_id: Optional[List[str]: List of Route IDs to select. If more than one is
            provided, the selection will be based on an OR condition. Can also select based on
            a partial match using the '*' wildcard character.
        trip_short_name: Optional[List[str]: List Trip short names to select. If more than one
            is provided, the selection will be based on an OR condition. Can also select based on
            a partial match using the '*' wildcard character.
    """

    model_config = ConfigDict(extra="allow", coerce_numbers_to_str=True)

    trip_id: Annotated[Optional[list[str]], Field(None, misn_length=1)]
    shape_id: Annotated[Optional[list[str]], Field(None, min_length=1)]
    direction_id: Optional[Literal[0, 1]] = None
    service_id: Annotated[Optional[list[str]], Field(None, min_length=1)]
    route_id: Annotated[Optional[list[str]], Field(None, min_length=1)]
    trip_short_name: Annotated[Optional[list[str]], Field(None, min_length=1)]

    class ConfigDict:
        """Config for the model."""

        protected_namespaces = ()


class SelectTransitLinks(BaseModel):
    """Requirements for describing multiple transit links of a project card.

    Attributes:
        model_link_id: Optional[List[int]]: List of model link IDs to select. If more than one is
            provided, the selection will be OR or AND based on the `require` attribute. Must
            be provided if `ab_nodes` is not.
        ab_nodes: Optional[List[TransitABNodes]]: List of AB nodes to select. If more than one is
            provided, the selection will be OR or AND based on the `require` attribute. Must
            be provided if `model_link_id` is not.
        require: Optional[Literal["any", "all"]]: Require either any or all of the selected
            links to meet the selection criteria.

    !!! Example "Example: Select transit trips with links using nodes 1-2 OR 3-4."
        ```yaml
        ab_nodes:
            - A: 1
              B: 2
            - A: 3
              B: 4
        require: any
        ```

    !!! Example "Example: Select transit trips with links using model link IDs 123 AND 321."
        ```yaml
        model_link_id: [123, 321]
        require: all
        ```
    """

    require_one_of: ClassVar = [
        ["ab_nodes", "model_link_id"],
    ]

    model_link_id: Annotated[Optional[list[int]], Field(min_length=1)]
    ab_nodes: Annotated[Optional[list[TransitABNodes]], Field(min_length=1)]
    require: Optional[Literal["any", "all"]]

    model_config = ConfigDict(
        extra="forbid",
        protected_namespaces=(),
    )
    _examples: ClassVar[list[dict]] = [
        {
            "ab_nodes": [{"A": 75520, "B": 66380}, {"A": 66380, "B": 75520}],
            "type": "any",
        },
        {
            "model_link_id": [123, 321],
            "type": "all",
        },
    ]


class SelectTransitNodes(BaseModel):
    """Selecting trips that use transit nodes.

    Attributes:
        stop_id: List[int]: List of model node IDs to select. Must have at least one node.
            Multiple nodes are treated as an OR or AND based on the `require` attribute.
        require: Optional[Literal["any", "all"]]: Require either any or all of the selected
            nodes to meet the selection criteria.

    !!! Example "Example: Select transit trips that use model node IDs 1 AND 2."
        ```yaml
        stop_id: [1, 2]
        require: all
        ```
    """

    stop_id: Annotated[list[int], Field(min_length=1)]
    require: Optional[Literal["any", "all"]] = "any"

    model_config = ConfigDict(
        extra="forbid",
    )


class SelectRoadNode(BaseModel):
    """Selection of a single roadway node in the `facility` section of a project card.

    Additional properties may be used if they are defined in the roadway network node table.

    Attributes:
        model_node_id: Optional[int]: Model node ID to select. Must have either this or
            `osm_node_id`.
        osm_node_id: Optional[str]: OSM node ID to select. Must have either this or
            `model_node_id`.

    !!! Example "Example: Select roadway node with model node ID 12345."
        ```yaml
        model_node_id: 12345
        ```
    """

    require_one_of: ClassVar = [["osm_node_id", "model_node_id"]]
    model_config = ConfigDict(extra="allow", coerce_numbers_to_str=True)

    osm_node_id: Optional[str]
    model_node_id: Optional[int]


class RoadNode(BaseModel):
    """Requirements for describing new roadway nodes of a project card.

    Attributes:
        model_node_id: int: Model node ID.
        X: Longitude: Longitude of the node.
        Y: Latitude: Latitude of the node.
    """

    model_node_id: int
    X: Longitude
    Y: Latitude


class RoadLink(BaseModel):
    """Requirements for describing new roadway links of a project card.

    The following fields may NOT be specified in a ProjectCard as they are calculated or managed
    by Wrangler: `model_link_id_idx`, `managed`, `geometry`, `projects`, `ML_geometry`, `ML_A`,
    `ML_B`, `ML_projects`.

    Attributes:
        model_link_id: int: Model link ID.
        A: int: `model_node_id` for the A (from) node.
        B: int: `model_node_id` for the B (to) node.
        name: str: Name of the link.
        roadway: OsmRoadwayType: Roadway facility type based on Open Street Map (OSM) roadway types.
            See: <https://wiki.openstreetmap.org/wiki/Key:highway>.
        lanes: int: Number of lanes. Must be greater than or equal to 0.
        price: Optional[float]: Price for the link.
        rail_only: Optional[bool]: True if the link is rail only.
        bus_only: Optional[bool]: True if the link is bus only.
        drive_access: Optional[bool]: True if the link is drive accessible.
        bike_access: Optional[bool]: True if the link is bike accessible.
        walk_access: Optional[bool]: True if the link is walk accessible.
        truck_access: Optional[bool]: True if the link is truck accessible.
        distance: float: Distance of the link in miles. Must be greater than or equal to 0.
        shape_id: Optional[str]: Shape ID for the link used as a foreign key to a
            roadway shape table.
        osm_link_id: Optional[str]: OSM link ID.
        access: Optional[Any]: Access for the link.
        sc_lanes: Optional[list[dict]]: List of values of the lane property as it changes with
            timespans and/or categories (e.g. HOV, truck, etc.).
        sc_price: Optional[list[dict]]: List of values of the price property as it changes with
            timespans and/or categories (e.g. HOV, truck, etc.).
        ML_access_point: Optional[MLAccessEgress]: Access point for parallel managed lanes.
        ML_egress_point: Optional[MLAccessEgress]: Egress point for parallel managed lanes.
        ML_lanes: Optional[int]: Number of lanes for parallel managed lanes. Must be greater than
            or equal to 0.
        ML_price: Optional[float]: Price for parallel managed lanes.
        ML_access: Optional[Any]: Access for parallel managed lanes.
        sc_ML_lanes: Optional[list[dict]]: List of values of the lane property for parallel managed
            lanes as it changes with timespans and/or categories (e.g. HOV, truck, etc.).
        sc_ML_price: Optional[list[dict]]: List of values of the price property for parallel managed
            lanes as it changes with timespans and/or categories (e.g. HOV, truck, etc.).

    !!! Example "Example Roadway Link"
        ```yaml
        - model_link_id: 404982
          A: 269066
          B: 268932
          name: new freeway
          roadway: motorway
          lanes: 3
          distance: 0.5
          sc_lanes:
            - timespan: ['6:00', '9:00']
              value: 2
            - timespan: ['9:00', '15:00']
              value: 4
          sc_price:
            - timespan: ['6:00', '9:00']
              value: 2.0
            - timespan: ['9:00', '15:00']
              value: 4.0
          ML_access_point: 'all'
          ML_egress_point: 'all'
          ML_lanes: 1
          sc_ML_lanes:
            - timespan: ['6:00', '9:00']
              value: 2
            - timespan: ['9:00', '15:00']
              value: 4
          sc_ML_price:
            - timespan: ['6:00', '9:00']
              value: 2.0
            - timespan: ['9:00', '15:00']
              value: 4.0
        ```
    """

    model_config = ConfigDict(coerce_numbers_to_str=True)
    PROTECTED_FIELDS: ClassVar = [
        "model_link_id_idx",
        "managed",
        "geometry",
        "projects",
        "ML_geometry",
        "ML_A",
        "ML_B",
        "ML_projects",
    ]
    model_link_id: int
    A: int
    B: int
    name: str
    roadway: OsmRoadwayType
    lanes: Annotated[int, Field(ge=0)]

    # Fields Wrangler has defaults for that are optional to specify in ProjectCard
    price: Optional[float]
    rail_only: Optional[bool]
    bus_only: Optional[bool]
    drive_access: Optional[bool]
    bike_access: Optional[bool]
    walk_access: Optional[bool]
    truck_access: Optional[bool]
    distance: Annotated[float, Field(ge=0)]

    # Optional Fields for Wrangler
    shape_id: Optional[str]
    osm_link_id: Optional[str]
    access: Optional[Any]
    sc_lanes: Optional[list[dict]]
    sc_price: Optional[list[dict]]

    # Fields for parallel managed lanes properties
    ML_access_point: Optional[MLAccessEgress]
    ML_egress_point: Optional[MLAccessEgress]

    ML_lanes: Optional[Annotated[int, Field(0, ge=0)]]
    ML_price: Optional[Annotated[float, Field(0)]]
    ML_access: Optional[Any]

    sc_ML_lanes: Optional[list[dict]]
    sc_ML_price: Optional[list[dict]]
    sc_ML_access: Optional[list[dict]]
    ML_shape_id: Optional[str]

    @model_validator(mode="before")
    @classmethod
    def check_protected_omitted(cls, data: Any) -> Any:
        """Check that protected fields are omitted."""
        if isinstance(data, dict):
            protected_present = [k for k in cls.PROTECTED_FIELDS if k in data]
            if protected_present:
                msg = f"Protected fields {cls.PROTECTED_FIELDS} must be omitted."
                CardLogger.error(msg + f" Found: {protected_present}")
                raise ValueError(msg)
        return data


class TransitRoutingChange_Routing(BaseModel):
    """Value for setting routing change for transit.

    Attributes:
        existing: list[int]: list of `model_node_id` for the extent of the existing nodes
            to change.
        set: list[int]: list of `model_node_id` for the extent of the new nodes to set.
            Nodes which are negative will be treated as non-stops.

    !!! Example "Example: Reroute around node 2."
        ```yaml
        routing:
            existing: [1, -2, 3]
            set: [1, -4, -5, -6,  3]
        ```
    """

    model_config = ConfigDict(extra="forbid")
    existing: list[int]
    set: list[int]


class TransitStopProps(BaseModel):
    """Representation of details about a single transit stop for a new route.

    Must have at at least either:

    - `stop`
    - `board` and `alight`

    - If `stop` is True, then `board` and `alight` are assumed to be True unless otherwise
    specified.
    - If `stop` is False, then `board` and `alight` are assumed to be False unless otherwise
    specified.

    Attributes:
        stop: Optional[bool]: True if the stop is a stop on the route.
        dwell_secs: Optional[PositiveInt]: Dwell time in seconds at the stop.
        time_to_next_node_sec: Optional[PositiveInt]: Time in seconds to the next node.
        board: Optional[bool]: True if the stop is a boarding stop.
        alight: Optional[bool]: True if the stop is an alighting stop.

    !!! Example "Example: Stop with only boarding."
        ```yaml
        alight: false
        board: true
        ```

    !!! Example "Example: Stop with no boarding or alighting."
        ```yaml
        stop: false
        ```

    !!! Example "Example: Stop with boarding and alighting."
        ```yaml
        stop: true
        time_to_next_node_sec: 68
        ```
    """

    require_one_of: ClassVar = [
        ["stop", "board"],
        ["stop", "alight"],
        ["stop"],
        ["board", "alight"],
    ]
    stop: Optional[bool]
    dwell_secs: Optional[PositiveInt]
    time_to_next_node_sec: Optional[PositiveInt]
    board: Optional[bool]
    alight: Optional[bool]


TransitStop = Annotated[dict[int, TransitStopProps], Field(min_length=1, max_length=1)]
TransitRouteNode = Union[int, TransitStop]
TransitRouting = Annotated[list[TransitRouteNode], Field(min_length=1)]

TransitHeadways = Annotated[
    dict[Timespan, PositiveInt],
    Field(min_length=1, max_length=1, examples=[{"('7:00', '9:00')": 600}]),
]


class TransitTrip(BaseModel):
    """Description of a new transit trip.

    Additional properties may be used so long as they do not conflict with the fields:
    `trip_id`, `shape_id`, and `route_id`. `route_id` is provided at the route-level and
    `trip_id`, `shape_id` are managed by Wrangler in order to ensure primary and foreign
    key constraints are met.

    Attributes:
        headway_secs: list[TransitHeadways]: List of headways for the trip - each of which is a
            dictionary of a single timespans and headway value. Must have at least one headway.
            Example: `{"('7:00', '9:00')": 600}`.
        routing: TransitRouting: Routing for the trip which is a list of nodes or detailed
            stop properties.
        service_id: Optional[str]: Service ID for the trip. See GTFS for more information:
            <https://gtfs.org/reference/static/#trips.txt>.
        trip_headsign: Optional[str]: Trip headsign. See GTFS for more information:
            <https://gtfs.org/reference/static/#trips.txt>.
        trip_short_name: Optional[str]: Trip short name. See GTFS for more information:
            <https://gtfs.org/reference/static/#trips.txt>.
        direction_id: Optional[int]: Direction ID for the trip. Must be either 0 or 1. See
            GTFS for more information: <https://gtfs.org/reference/static/#trips.txt>.

    !!! Example "Example: New Transit Trip"
        ```yaml
        - route_id: 1
          service_id: weekday
          trip_headsign: downtown
          trip_short_name: 1
          direction_id: 0
          headway_secs:
            - ('6:00', '12:00'): 600
            - ('12:00', '13:00'): 900
          routing:
            - 1:
                stop: true
            - 2
            - 3
            - 4:
                stop: true
                alight: false
            - 5
            - 6:
                stop: true
        ```
    """

    model_config = ConfigDict(coerce_numbers_to_str=True)
    PROTECTED_FIELDS: ClassVar = ["trip_id", "shape_id", "route_id"]
    headway_secs: Annotated[list[TransitHeadways], Field(min_length=1)]
    routing: TransitRouting
    service_id: Optional[str]
    trip_headsign: Optional[str]
    trip_short_name: Optional[str]
    direction_id: Optional[int]


class TransitRoute(BaseModel):
    """Description of a new transit route.

    Attributes:
        route_id: str: Route ID for the route.
        agency_id: str: Agency ID for the route. See GTFS for more information:
            <https://gtfs.org/reference/static/#routes.txt>.
        route_short_name: Optional[str]: Route short name for the route. See GTFS for more
            information: <https://gtfs.org/reference/static/#routes.txt>.
        route_long_name: Optional[str]: Route long name for the route.  See GTFS for more
            information: <https://gtfs.org/reference/static/#routes.txt>.
        route_type: int: Route type for the route. See GTFS for more information:
            <https://gtfs.org/reference/static/#routes.txt>.
        trips: list[TransitTrip]: List of trips for the route. Must have at least one trip.
    """

    model_config = ConfigDict(coerce_numbers_to_str=True)
    route_id: str
    agency_id: str
    route_short_name: Optional[str]
    route_long_name: Optional[str]
    route_type: int
    trips: Annotated[list[TransitTrip], Field(min_length=1)]
