from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, BeforeValidator
from typing_extensions import Annotated


class GroupItem(BaseModel):
    category: List[str]
    value: Annotated[float, Field(ge=0.0)]


class ByAccessCategory(BaseModel):
    default: Annotated[float, Field(ge=0.0)]
    group: Optional[List[GroupItem]] = None


class TimeofdayItem(BaseModel):
    category: List[str]
    timespan: Timespan
    value: Annotated[float, Field(ge=0.0)]


class ByAccessCategoryAndTimeOfDay(BaseModel):
    default: Annotated[float, Field(ge=0.0)]
    timeofday: List[TimeofdayItem]


class TimeofdayItemModel(BaseModel):
    timespan: Timespan
    value: Annotated[float, Field(ge=0.0)]


class ByTimeOfDay(BaseModel):
    default: Annotated[float, Field(ge=0.0)]
    timeofday: List[TimeofdayItemModel]


class SelfObjType(Enum):
    """
    For calculated project cards, must refer to the object to perform the calculation on.
    """

    RoadwayNetwork = "RoadwayNetwork"
    TransitNetwork = "TransitNetwork"


class Dependencies(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prerequisites: Annotated[
        Optional[List],
        Field(None, examples=["7th St E Road Diet"], title="Project Prerequisites"),
    ]
    corequisites: Annotated[
        Optional[List],
        Field(None, examples=["7th St E Road Diet"], title="Project Co-requisites"),
    ]
    conflicts: Annotated[
        Optional[List],
        Field(None, examples=["7th St E Road Diet"], title="Project Conflicts"),
    ]

    class ConfigDict:
        protected_namespaces = ()


class Tag(RootModel[str]):
    root: Annotated[str, BeforeValidator(str), Field(examples=["vision2050"])]


class Tags(RootModel[List[Tag]]):
    root: Annotated[List[Tag], Field(title="Project Tags")]


class All(Enum):
    True_ = "True"
    False_ = "False"


class Name(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="Name of Roadway facility. If multiple, can be contatenated with a comma.",
            examples=[
                "Elm Street",
                "Raleigh Beltline",
                "Capital Beltway",
                "3rd St,Willie Mays Blvd",
            ],
        ),
    ]


class Node(RootModel[int]):
    root: Annotated[int, Field(description="Foreign key to the nodes object.")]


class IntersectionId(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="The Intersectionid Schema",
            examples=["4d0231aa0ebb779f142c2518703ee481"],
        ),
    ]


class ShstReferenceIdLink(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="The Shstreferenceid Schema",
            examples=["6a22969708104ae2497244f3d079381d"],
        ),
    ]


class ShstGeometryId(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="The Shstgeometryid Schema",
            examples=["6a22969708104ae2497244f3d079381d"],
        ),
    ]


class Bearing(RootModel[int]):
    root: Annotated[
        int,
        Field(
            description="The angle of the eminating arc from the point, expressed in clockwise degrees from North (0)",
            examples=[0, 90, 275],
            ge=0,
            le=360,
        ),
    ]


class Point(RootModel[Any]):
    root: Any


class Distance(RootModel[float]):
    root: Annotated[
        float,
        Field(
            description="Distance of facility in miles. If not provided, will be calculated provided nodes",
            examples=[93.08],
            ge=0.0,
            title="Distance",
        ),
    ]


class Ref(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="Reference name of roadway, per Open Street Map definition.",
            examples=["I-40", "US66", "WA520"],
        ),
    ]


class ModelLinkId(RootModel[int]):
    root: Annotated[int, Field(description="Unique id for facility.")]


class OsmLinkId(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="Reference to the corresponding Open Street Map link. Note that due to link splitting this may or may not be unique, and is not a required attribute."
        ),
    ]


class Roadway(Enum):
    """
    Roadway type, using [OSM Highway values](https://wiki.openstreetmap.org/wiki/Key:highway#Roads). Notes: * `X_link` roadway types denote linkage roads going to/from roadway type X (i.e. on/off ramps, etc). * `road` denotes unknown type.
    """

    motorway = "motorway"
    trunk = "trunk"
    primary = "primary"
    secondary = "secondary"
    tertiary = "tertiary"
    unclassified = "unclassified"
    residential = "residential"
    motorway_link = "motorway_link"
    trunk_link = "trunk_link"
    primary_link = "primary_link"
    secondary_link = "secondary_link"
    tertiary_link = "tertiary_link"
    living_street = "living_street"
    service = "service"
    pedestrian = "pedestrian"
    footway = "footway"
    steps = "steps"
    cycleway = "cycleway"
    track = "track"
    bus_guideway = "bus_guideway"
    road = "road"


class LocationReference(BaseModel):
    sequence: Annotated[int, Field(ge=0)]
    point: Point
    distanceToNextRef: Optional[Distance] = None
    bearing: Optional[Bearing] = None
    intersectionId: Optional[IntersectionId] = None


class LocationReferences(RootModel[List[LocationReference]]):
    """
    The Locationreferences Schema
    """

    root: Annotated[
        List[LocationReference], Field(description="The Locationreferences Schema")
    ]


class Lanes1(RootModel[float]):
    root: Annotated[
        float,
        Field(
            description="Number of lanes either in simple or complex terms.",
            examples=[
                2,
                5,
                {"default": 1, "timeofday": {"timespan": ["6:00", "9:00"], "value": 2}},
            ],
            ge=0.0,
        ),
    ]


class Time(RootModel[str]):
    root: Annotated[
        str,
        Field(
            examples=["12:34", "12:34:56"],
            pattern="^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$",
        ),
    ]


class Price1(RootModel[float]):
    root: Annotated[
        float,
        Field(
            description="Price of facility, either as a positive number of a complex type by time of day and/or access category.",
            examples=[
                0.75,
                2.9,
                {"default": 1, "timeofday": {"time": ["6:00", "9:00"], "value": 2}},
            ],
            ge=0.0,
        ),
    ]


class WalkAccess(RootModel[Union[int, bool]]):
    root: Annotated[
        Union[int, bool],
        Field(
            description="Indicates if a facility is generally available for pedestrians. Must not be true if any of bus_only or rail_only are true."
        ),
    ]


class BikeAccess(RootModel[Union[int, bool]]):
    root: Annotated[
        Union[int, bool],
        Field(
            description="Indicates if a facility is generally available for cyclists. Must not be true if any of bus_only or rail_only are true."
        ),
    ]


class BikeFacility(RootModel[int]):
    root: Annotated[
        int,
        Field(
            description="Indicator for the category of bicycle facility on or along the roadway. If null, indicates unknown. If zero, indicates no facility.",
            ge=0,
        ),
    ]


class DriveAccess(RootModel[Union[int, bool]]):
    root: Annotated[
        Union[int, bool],
        Field(
            description="Indicates if a facility is generally available for driving. Must not be true if any of bus_only or rail_only are true."
        ),
    ]


class BusOnly(RootModel[Union[int, bool]]):
    root: Annotated[
        Union[int, bool],
        Field(
            description="Indicates if a facility is rail-only if True.  Must not be true if any of walk_access, bike_access, drive_access, rail_only are True."
        ),
    ]


class RailOnly(RootModel[Union[int, bool]]):
    root: Annotated[
        Union[int, bool],
        Field(
            description="Indicates if a facility is rail-only if True.  Must not be true if any of walk_access, bike_access, drive_access, bus_only are True."
        ),
    ]


class SegmentId(RootModel[Union[str, int]]):
    root: Annotated[
        Union[str, int],
        Field(
            description="An identifier for segments of roadway. Can be useful for querying and setting values for parts of facilities, summary scripts, etc."
        ),
    ]


class MLAccessEgress1(RootModel[List[Any]]):
    root: Annotated[
        List[Any],
        Field(
            description="Indicates where a managed lane facility can by accessed or exited either by indicating `all` for everywhere, or listing foreign keys to specific A-nodes.",
            examples=["all", [123, 5543]],
            min_length=1,
        ),
    ]


class MLAccessEgress(RootModel[Union[str, MLAccessEgress1]]):
    root: Annotated[
        Union[str, MLAccessEgress1],
        Field(
            description="Indicates where a managed lane facility can by accessed or exited either by indicating `all` for everywhere, or listing foreign keys to specific A-nodes.",
            examples=["all", [123, 5543]],
        ),
    ]


class Mode(Enum):
    drive = "drive"
    walk = "walk"
    bike = "bike"
    transit = "transit"
    any = "any"


class OsmNodeId(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="Reference to the corresponding Open Street Map node.",
            examples=["954734870"],
        ),
    ]


class ModelNodeId(RootModel[int]):
    root: Annotated[int, Field(description="Primary key to the nodes object.")]


class X(RootModel[float]):
    root: Annotated[float, Field(description="X coordinate (e.g. Longitude)")]


class Y(RootModel[float]):
    root: Annotated[float, Field(description="Y coordinate (e.g. Latitude)")]


class Z(RootModel[float]):
    root: Annotated[float, Field(description="Z coordinate (e.g. Altitude)")]


class ShstReferenceIdNode(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="Shared streets node ID reference.",
            examples=["0751f5ce12472360fed0d0e80ceae35c"],
        ),
    ]


class WalkNode(RootModel[Union[int, bool]]):
    root: Annotated[
        Union[int, bool],
        Field(
            description="Indicates node is part of the pedestrian network. Useful for exporting or querying networks by mode."
        ),
    ]


class BikeNode(RootModel[Union[int, bool]]):
    root: Annotated[
        Union[int, bool],
        Field(
            description="Indicates node is part of the bike network. Useful for exporting or querying networks by mode."
        ),
    ]


class DriveNode(RootModel[Union[int, bool]]):
    root: Annotated[
        Union[int, bool],
        Field(
            description="Indicates node is part of the driving network. Useful for exporting or querying networks by mode."
        ),
    ]


class TransitNode(RootModel[Union[int, bool]]):
    root: Annotated[
        Union[int, bool],
        Field(
            description="Indicates node is part of the transit network. Useful for exporting or querying networks by mode."
        ),
    ]


class RoadwayNode(BaseModel):
    """
    Requirements for roadway nodes.
    """

    model_node_id: ModelNodeId
    osm_node_id: Optional[OsmNodeId] = None
    shstReferenceId: Optional[ShstReferenceIdNode] = None
    outboundReferenceIds: Optional[List[ShstReferenceIdLink]] = None
    inboundReferenceIds: Optional[List[ShstReferenceIdLink]] = None
    walk_node: Optional[WalkNode] = None
    bike_node: Optional[BikeNode] = None
    drive_node: Optional[DriveNode] = None
    transit_node: Optional[TransitNode] = None
    X: X
    Y: Y
    Z: Optional[Z] = None


class Point1(RootModel[List[Z]]):
    """
    The Point Schema
    """

    root: Annotated[
        List[Z], Field(description="The Point Schema", max_length=3, min_length=2)
    ]


class PropertyChanges1(RootModel[Dict[str, Any]]):
    root: Annotated[Dict[str, Any], Field(min_length=1)]


class SelectNode1(BaseModel):
    """
    Selection of a single roadway node in the `facility` section of a project card.
    """

    model_config = ConfigDict(extra="forbid")
    osm_node_id: OsmNodeId
    model_node_id: Optional[ModelNodeId] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectNode2(BaseModel):
    """
    Selection of a single roadway node in the `facility` section of a project card.
    """

    model_config = ConfigDict(extra="forbid")
    osm_node_id: Optional[OsmNodeId] = None
    model_node_id: ModelNodeId

    class ConfigDict:
        protected_namespaces = ()


class SelectNode(RootModel[Union[SelectNode1, SelectNode2]]):
    root: Annotated[
        Union[SelectNode1, SelectNode2],
        Field(
            description="Selection of a single roadway node in the `facility` section of a project card.",
            examples=[{"osm_node_id": "12345"}, {"model_node_id": 67890}],
            title="Single roadway network node",
        ),
    ]


class PropertySet1(BaseModel):
    existing: Optional[Union[float, str]] = None
    change: Union[float, str]
    set: Optional[Union[float, str]] = None


class PropertySet2(BaseModel):
    existing: Optional[Union[float, str]] = None
    change: Optional[Union[float, str]] = None
    set: Union[float, str]


class PropertySet(RootModel[Union[PropertySet1, PropertySet2]]):
    root: Union[PropertySet1, PropertySet2]


class TripId(RootModel[str]):
    root: Annotated[
        str, Field(description="ID for Individual trip a transit vehicle takes..")
    ]


class ShapeId(RootModel[str]):
    root: Annotated[
        str, BeforeValidator(str), Field(description="ID for shape trip is following.")
    ]


class ServiceId(RootModel[str]):
    root: Annotated[
        str, BeforeValidator(str), Field(description="ID for service schedule.")
    ]


class TripShortName(RootModel[str]):
    root: Annotated[
        str, Field(description="Route short name, often something like `38X`.")
    ]


class TripHeadsign(RootModel[str]):
    root: Annotated[str, BeforeValidator(str), Field(description="Trip Headsign.")]


class DirectionId(Enum):
    """
    Consistent with GTFS definition defining outbound vs inbound routes.
    """

    integer_0 = 0
    integer_1 = 1


class HeadwaySecs(RootModel[int]):
    root: Annotated[int, Field(description="Headway between trips in seconds.")]


class Routing(RootModel[List[int]]):
    """
    List of nodes that the trip traverses with a `-` in front of nodes where the service does not stop.
    """

    root: Annotated[
        List[int],
        Field(
            description="List of nodes that the trip traverses with a `-` in front of nodes where the service does not stop."
        ),
    ]


class RouteId(RootModel[str]):
    root: Annotated[
        str, BeforeValidator(str), Field(description="ID for general route.")
    ]


class AgencyId(RootModel[str]):
    root: Annotated[str, BeforeValidator(str), Field(description="ID for agency.")]


class RouteShortName(RootModel[str]):
    root: Annotated[str, BeforeValidator(str), Field(description="Route short name.")]


class RouteLongName(RootModel[str]):
    root: Annotated[str, BeforeValidator(str), Field(description="Route long name.")]


class RouteType(Enum):
    """
    Route type.
    """

    integer_0 = 0
    integer_1 = 1
    integer_2 = 2
    integer_3 = 3
    integer_4 = 4
    integer_5 = 5
    integer_6 = 6
    integer_7 = 7
    integer_11 = 11
    integer_12 = 12


class SelectRouteProperties(BaseModel):
    """
    Selection proeprties for transit routes.
    """

    model_config = ConfigDict(extra="allow")
    route_short_name: Annotated[
        Optional[List[RouteShortName]], Field(None, min_length=1)
    ]
    route_long_name: Annotated[Optional[List[RouteLongName]], Field(None, min_length=1)]
    agency_id: Annotated[Optional[List[AgencyId]], Field(None, min_length=1)]
    route_type: Annotated[Optional[List[RouteType]], Field(None, min_length=1)]

    class ConfigDict:
        protected_namespaces = ()


class Require(Enum):
    any = "any"
    all = "all"


class StopId(RootModel[str]):
    root: Annotated[
        str, BeforeValidator(str), Field(description="ID for specific transit stop.")
    ]


class Routing1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    existing: Optional[List] = None
    set: List

    class ConfigDict:
        protected_namespaces = ()


class Pycode(RootModel[str]):
    root: str


class SelectLinks1(BaseModel):
    """
    requirements for describing links in the `facility` section of a project card.
    """

    model_config = ConfigDict(extra="allow")
    all: Optional[All] = None
    name: Annotated[List[Name], Field(min_length=1)]
    ref: Annotated[Optional[List[Ref]], Field(None, min_length=1)]
    osm_link_id: Annotated[Optional[List[OsmLinkId]], Field(None, min_length=1)]
    model_link_id: Annotated[Optional[List[ModelLinkId]], Field(None, min_length=1)]
    modes: Optional[List[Mode]] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectLinks2(BaseModel):
    """
    requirements for describing links in the `facility` section of a project card.
    """

    model_config = ConfigDict(extra="allow")
    all: Optional[All] = None
    name: Annotated[Optional[List[Name]], Field(None, min_length=1)]
    ref: Annotated[List[Ref], Field(min_length=1)]
    osm_link_id: Annotated[Optional[List[OsmLinkId]], Field(None, min_length=1)]
    model_link_id: Annotated[Optional[List[ModelLinkId]], Field(None, min_length=1)]
    modes: Optional[List[Mode]] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectLinks3(BaseModel):
    """
    requirements for describing links in the `facility` section of a project card.
    """

    model_config = ConfigDict(extra="allow")
    all: Optional[All] = None
    name: Annotated[Optional[List[Name]], Field(None, min_length=1)]
    ref: Annotated[Optional[List[Ref]], Field(None, min_length=1)]
    osm_link_id: Annotated[List[OsmLinkId], Field(min_length=1)]
    model_link_id: Annotated[Optional[List[ModelLinkId]], Field(None, min_length=1)]
    modes: Optional[List[Mode]] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectLinks4(BaseModel):
    """
    requirements for describing links in the `facility` section of a project card.
    """

    model_config = ConfigDict(extra="allow")
    all: Optional[All] = None
    name: Annotated[Optional[List[Name]], Field(None, min_length=1)]
    ref: Annotated[Optional[List[Ref]], Field(None, min_length=1)]
    osm_link_id: Annotated[Optional[List[OsmLinkId]], Field(None, min_length=1)]
    model_link_id: Annotated[List[ModelLinkId], Field(min_length=1)]
    modes: Optional[List[Mode]] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectLinks5(BaseModel):
    """
    requirements for describing links in the `facility` section of a project card.
    """

    model_config = ConfigDict(extra="allow")
    all: All
    name: Annotated[Optional[List[Name]], Field(None, min_length=1)]
    ref: Annotated[Optional[List[Ref]], Field(None, min_length=1)]
    osm_link_id: Annotated[Optional[List[OsmLinkId]], Field(None, min_length=1)]
    model_link_id: Annotated[Optional[List[ModelLinkId]], Field(None, min_length=1)]
    modes: Optional[List[Mode]] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectLinks(
    RootModel[
        Union[SelectLinks1, SelectLinks2, SelectLinks3, SelectLinks4, SelectLinks5]
    ]
):
    root: Annotated[
        Union[SelectLinks1, SelectLinks2, SelectLinks3, SelectLinks4, SelectLinks5],
        Field(
            description="requirements for describing links in the `facility` section of a project card.",
            examples=[
                {"name": ["Main St"], "modes": ["drive"]},
                {"osm_link_id": ["123456789"]},
                {"model_link_id": [123456789], "modes": ["walk"]},
                {"all": "True", "modes": ["transit"]},
            ],
            title="Roadway link selection",
        ),
    ]


class Timespan(RootModel[List[Time]]):
    root: Annotated[
        List[Time], Field(examples=[["12:00", "19:45:00"]], max_length=2, min_length=2)
    ]


class SelectNodes1(BaseModel):
    """
    requirements for describing multiple nodes of a project card (e.g. to delete).
    """

    model_config = ConfigDict(extra="forbid")
    osm_node_id: Annotated[List[OsmNodeId], Field(min_length=1)]
    model_node_id: Annotated[Optional[List[ModelNodeId]], Field(None, min_length=1)]
    ignore_missing: Optional[bool] = None
    all: Optional[bool] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectNodes2(BaseModel):
    """
    requirements for describing multiple nodes of a project card (e.g. to delete).
    """

    model_config = ConfigDict(extra="forbid")
    osm_node_id: Annotated[Optional[List[OsmNodeId]], Field(None, min_length=1)]
    model_node_id: Annotated[List[ModelNodeId], Field(min_length=1)]
    ignore_missing: Optional[bool] = None
    all: Optional[bool] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectNodes(RootModel[Union[SelectNodes1, SelectNodes2]]):
    root: Annotated[
        Union[SelectNodes1, SelectNodes2],
        Field(
            description="requirements for describing multiple nodes of a project card (e.g. to delete).",
            examples=[
                {"osm_node_id": ["12345", "67890"], "model_node_id": [12345, 67890]},
                {"osm_node_id": ["12345", "67890"]},
                {"model_node_id": [12345, 67890]},
            ],
            title="Roadway network node",
        ),
    ]


class PropertyChanges(RootModel[Dict[str, PropertySet]]):
    root: Annotated[Dict[str, PropertySet], Field(min_length=1)]


class SelectSegment1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    links: SelectLinks
    nodes: Optional[SelectNodes] = None
    from_: Annotated[SelectNode, Field(alias="from")]
    to: SelectNode

    class ConfigDict:
        protected_namespaces = ()


class SelectSegment2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    links: SelectLinks
    nodes: Optional[SelectNodes] = None
    from_: Annotated[Optional[SelectNode], Field(None, alias="from")]
    to: Optional[SelectNode] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectSegment3(BaseModel):
    model_config = ConfigDict(extra="forbid")
    links: Optional[SelectLinks] = None
    nodes: SelectNodes
    from_: Annotated[Optional[SelectNode], Field(None, alias="from")]
    to: Optional[SelectNode] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectSegment(RootModel[Union[SelectSegment1, SelectSegment2, SelectSegment3]]):
    root: Annotated[
        Union[SelectSegment1, SelectSegment2, SelectSegment3],
        Field(
            examples=[
                {
                    "links": {"name": ["Main Street"]},
                    "from": {"model_node_id": 1},
                    "to": {"model_node_id": 2},
                },
                {"nodes": {"osm_node_id": ["1", "2", "3"]}},
                {"nodes": {"model_node_id": [1, 2, 3]}},
                {"links": {"model_link_id": [1, 2, 3]}},
            ],
            title="Roadway Facility Selection",
        ),
    ]


class SelectTripProperties(BaseModel):
    """
    Selection properties for transit trips.
    """

    model_config = ConfigDict(extra="allow")
    trip_id: Annotated[Optional[List[TripId]], Field(None, min_length=1)]
    shape_id: Annotated[Optional[List[ShapeId]], Field(None, min_length=1)]
    direction_id: Optional[DirectionId] = None
    service_id: Annotated[Optional[List[ServiceId]], Field(None, min_length=1)]
    route_id: Annotated[Optional[List[RouteId]], Field(None, min_length=1)]
    trip_short_name: Annotated[Optional[List[TripShortName]], Field(None, min_length=1)]

    class ConfigDict:
        protected_namespaces = ()


class SelectNodes3(BaseModel):
    """
    requirements for describing multiple transit nodes of a project card (e.g. to delete).
    """

    model_config = ConfigDict(extra="forbid")
    stop_id: Annotated[List[StopId], Field(min_length=1)]
    model_node_id: Annotated[Optional[List[ModelNodeId]], Field(None, min_length=1)]
    require: Optional[Require] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectNodes4(BaseModel):
    """
    requirements for describing multiple transit nodes of a project card (e.g. to delete).
    """

    model_config = ConfigDict(extra="forbid")
    stop_id: Annotated[Optional[List[StopId]], Field(None, min_length=1)]
    model_node_id: Annotated[List[ModelNodeId], Field(min_length=1)]
    require: Optional[Require] = None

    class ConfigDict:
        protected_namespaces = ()


class SelectNodesModel(RootModel[Union[SelectNodes3, SelectNodes4]]):
    root: Annotated[
        Union[SelectNodes3, SelectNodes4],
        Field(
            description="requirements for describing multiple transit nodes of a project card (e.g. to delete).",
            examples=[
                {"stop_id": ["stop1", "stop2"], "require": "any"},
                {"model_node_id": [1, 2], "require": "all"},
            ],
            title="Transit network nodes",
        ),
    ]


class RoadwayDeletion1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    links: SelectLinks
    nodes: Optional[SelectNodes] = None

    class ConfigDict:
        protected_namespaces = ()


class RoadwayDeletion2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    links: Optional[SelectLinks] = None
    nodes: SelectNodes

    class ConfigDict:
        protected_namespaces = ()


class RoadwayDeletion(RootModel[Union[RoadwayDeletion1, RoadwayDeletion2]]):
    root: Annotated[
        Union[RoadwayDeletion1, RoadwayDeletion2],
        Field(
            examples=[
                {"links": {"model_link_id": [1, 2, 3]}},
                {"links": {"ref": ["I-5"], "lanes": 2}},
                {"nodes": {"model_node_id": [1, 2, 3]}},
            ]
        ),
    ]


class ScopedNumberPropertyValue(
    RootModel[Union[ByTimeOfDay, ByAccessCategory, ByAccessCategoryAndTimeOfDay]]
):
    root: Union[ByTimeOfDay, ByAccessCategory, ByAccessCategoryAndTimeOfDay]


class Lanes(RootModel[Union[Lanes1, ScopedNumberPropertyValue]]):
    root: Annotated[
        Union[Lanes1, ScopedNumberPropertyValue],
        Field(
            description="Number of lanes either in simple or complex terms.",
            examples=[
                2,
                5,
                {"default": 1, "timeofday": {"timespan": ["6:00", "9:00"], "value": 2}},
            ],
        ),
    ]


class MLLanes(RootModel[Lanes]):
    root: Annotated[
        Lanes, Field(description="Lanes for a parallel managed lane facility.")
    ]


class Price(RootModel[Union[Price1, ScopedNumberPropertyValue]]):
    root: Annotated[
        Union[Price1, ScopedNumberPropertyValue],
        Field(
            description="Price of facility, either as a positive number of a complex type by time of day and/or access category.",
            examples=[
                0.75,
                2.9,
                {"default": 1, "timeofday": {"time": ["6:00", "9:00"], "value": 2}},
            ],
        ),
    ]


class MLPrice(RootModel[Price]):
    root: Annotated[
        Price, Field(description="Price for a parallel managed lane facility.")
    ]


class RoadwayLink(BaseModel):
    """
    Requirements for roadway links.
    """

    A: Node
    B: Node
    model_link_id: ModelLinkId
    osm_link_id: Optional[OsmLinkId] = None
    shstReferenceId: Optional[ShstReferenceIdLink] = None
    shstGeometryId: Optional[ShstGeometryId] = None
    locationReferences: Optional[LocationReferences] = None
    name: Name
    ref: Optional[Ref] = None
    roadway: Roadway
    lanes: Lanes
    price: Optional[Price] = None
    ML_lanes: Optional[Lanes] = None
    ML_price: Optional[MLPrice] = None
    ML_access_point: Optional[MLAccessEgress] = None
    ML_egress_point: Optional[MLAccessEgress] = None
    walk_access: WalkAccess
    bike_access: BikeAccess
    bike_facility: Optional[BikeFacility] = None
    drive_access: DriveAccess
    bus_only: Optional[BusOnly] = None
    rail_only: Optional[RailOnly] = None
    segment_id: Optional[SegmentId] = None
    ignore_missing: Optional[bool] = None
    all: Optional[bool] = None


class RoadwayPropertyChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    facility: SelectSegment
    property_changes: Union[PropertyChanges, PropertyChanges1]

    class ConfigDict:
        protected_namespaces = ()


class SelectTrips(BaseModel):
    model_config = ConfigDict(extra="forbid")
    trip_properties: Optional[SelectTripProperties] = None
    route_properties: Optional[SelectRouteProperties] = None
    timespans: Annotated[Optional[List[Timespan]], Field(None, min_length=1)]
    nodes: Optional[SelectNodesModel] = None

    class ConfigDict:
        protected_namespaces = ()


class TransitRoutingChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: SelectTrips
    routing: Routing1

    class ConfigDict:
        protected_namespaces = ()


class ChangeRoadwayDeletion(RootModel[RoadwayDeletion]):
    root: RoadwayDeletion


class RoadwayAddition1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    links: List[RoadwayLink]
    nodes: Optional[List[RoadwayNode]] = None

    class ConfigDict:
        protected_namespaces = ()


class RoadwayAddition2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    links: Optional[List[RoadwayLink]] = None
    nodes: List[RoadwayNode]

    class ConfigDict:
        protected_namespaces = ()


class RoadwayAddition(RootModel[Union[RoadwayAddition1, RoadwayAddition2]]):
    root: Annotated[
        Union[RoadwayAddition1, RoadwayAddition2],
        Field(
            examples=[
                {
                    "links": [
                        {
                            "A": 1,
                            "B": 2,
                            "model_link_id": 123,
                            "name": "Elm Street",
                            "roadway": "residential",
                            "lanes": 2,
                            "price": 0.75,
                            "walk_access": 1,
                            "bike_access": 1,
                            "bike_facility": 1,
                            "drive_access": 1,
                            "bus_only": 0,
                            "rail_only": 0,
                        }
                    ],
                    "nodes": [
                        {"model_node_id": 1, "X": -122.419, "Y": 37.7},
                        {"model_node_id": 2, "X": -122.419, "Y": 37.8},
                    ],
                }
            ]
        ),
    ]


class ChangeRoadwayPropertyChange(RootModel[RoadwayPropertyChange]):
    root: RoadwayPropertyChange


class TransitPropertyChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: SelectTrips
    property_changes: Dict[str, PropertySet]

    class ConfigDict:
        protected_namespaces = ()


class ChangeRoadwayAddition(RootModel[RoadwayAddition]):
    root: RoadwayAddition


class Change1(BaseModel):
    roadway_deletion: ChangeRoadwayDeletion
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None


class Change2(BaseModel):
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: ChangeRoadwayAddition
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None


class Change3(BaseModel):
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: ChangeRoadwayPropertyChange
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None


class Change4(BaseModel):
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: TransitPropertyChange
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None


class Change5(BaseModel):
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: TransitRoutingChange
    pycode: Optional[Pycode] = None


class Change6(BaseModel):
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Pycode


class Change(RootModel[Union[Change1, Change2, Change3, Change4, Change5, Change6]]):
    root: Union[Change1, Change2, Change3, Change4, Change5, Change6]


class ProjectCardModel1(BaseModel):
    field_schema: Annotated[
        Optional[str],
        Field(
            None,
            alias="$schema",
            description="Reference to the project card schema which this file uses. If not specified, will be assumed to be the most recent release.",
        ),
    ]
    project: Annotated[
        str, Field(description="A project name which uniquely identifies this project")
    ]
    dependencies: Optional[Dependencies] = None
    tags: Optional[Tags] = None
    roadway_deletion: ChangeRoadwayDeletion
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    roadway_managed_lanes: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None
    changes: Optional[List[Change]] = None
    self_obj_type: Annotated[
        Optional[SelfObjType],
        Field(
            None,
            description="For calculated project cards, must refer to the object to perform the calculation on. ",
        ),
    ]
    notes: Optional[str] = None


class ProjectCardModel2(BaseModel):
    field_schema: Annotated[
        Optional[str],
        Field(
            None,
            alias="$schema",
            description="Reference to the project card schema which this file uses. If not specified, will be assumed to be the most recent release.",
        ),
    ]
    project: Annotated[
        str, Field(description="A project name which uniquely identifies this project")
    ]
    dependencies: Optional[Dependencies] = None
    tags: Optional[Tags] = None
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: ChangeRoadwayAddition
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    roadway_managed_lanes: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None
    changes: Optional[List[Change]] = None
    self_obj_type: Annotated[
        Optional[SelfObjType],
        Field(
            None,
            description="For calculated project cards, must refer to the object to perform the calculation on. ",
        ),
    ]
    notes: Optional[str] = None


class ProjectCardModel3(BaseModel):
    field_schema: Annotated[
        Optional[str],
        Field(
            None,
            alias="$schema",
            description="Reference to the project card schema which this file uses. If not specified, will be assumed to be the most recent release.",
        ),
    ]
    project: Annotated[
        str, Field(description="A project name which uniquely identifies this project")
    ]
    dependencies: Optional[Dependencies] = None
    tags: Optional[Tags] = None
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: ChangeRoadwayPropertyChange
    roadway_managed_lanes: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None
    changes: Optional[List[Change]] = None
    self_obj_type: Annotated[
        Optional[SelfObjType],
        Field(
            None,
            description="For calculated project cards, must refer to the object to perform the calculation on. ",
        ),
    ]
    notes: Optional[str] = None


class ProjectCardModel4(BaseModel):
    field_schema: Annotated[
        Optional[str],
        Field(
            None,
            alias="$schema",
            description="Reference to the project card schema which this file uses. If not specified, will be assumed to be the most recent release.",
        ),
    ]
    project: Annotated[
        str, Field(description="A project name which uniquely identifies this project")
    ]
    dependencies: Optional[Dependencies] = None
    tags: Optional[Tags] = None
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    roadway_managed_lanes: ChangeRoadwayPropertyChange
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None
    changes: Optional[List[Change]] = None
    self_obj_type: Annotated[
        Optional[SelfObjType],
        Field(
            None,
            description="For calculated project cards, must refer to the object to perform the calculation on. ",
        ),
    ]
    notes: Optional[str] = None


class ProjectCardModel5(BaseModel):
    field_schema: Annotated[
        Optional[str],
        Field(
            None,
            alias="$schema",
            description="Reference to the project card schema which this file uses. If not specified, will be assumed to be the most recent release.",
        ),
    ]
    project: Annotated[
        str, Field(description="A project name which uniquely identifies this project")
    ]
    dependencies: Optional[Dependencies] = None
    tags: Optional[Tags] = None
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    roadway_managed_lanes: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: TransitPropertyChange
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None
    changes: Optional[List[Change]] = None
    self_obj_type: Annotated[
        Optional[SelfObjType],
        Field(
            None,
            description="For calculated project cards, must refer to the object to perform the calculation on. ",
        ),
    ]
    notes: Optional[str] = None


class ProjectCardModel6(BaseModel):
    field_schema: Annotated[
        Optional[str],
        Field(
            None,
            alias="$schema",
            description="Reference to the project card schema which this file uses. If not specified, will be assumed to be the most recent release.",
        ),
    ]
    project: Annotated[
        str, Field(description="A project name which uniquely identifies this project")
    ]
    dependencies: Optional[Dependencies] = None
    tags: Optional[Tags] = None
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    roadway_managed_lanes: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: TransitRoutingChange
    pycode: Optional[Pycode] = None
    changes: Optional[List[Change]] = None
    self_obj_type: Annotated[
        Optional[SelfObjType],
        Field(
            None,
            description="For calculated project cards, must refer to the object to perform the calculation on. ",
        ),
    ]
    notes: Optional[str] = None


class ProjectCardModel7(BaseModel):
    field_schema: Annotated[
        Optional[str],
        Field(
            None,
            alias="$schema",
            description="Reference to the project card schema which this file uses. If not specified, will be assumed to be the most recent release.",
        ),
    ]
    project: Annotated[
        str, Field(description="A project name which uniquely identifies this project")
    ]
    dependencies: Optional[Dependencies] = None
    tags: Optional[Tags] = None
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    roadway_managed_lanes: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Pycode
    changes: Optional[List[Change]] = None
    self_obj_type: Annotated[
        Optional[SelfObjType],
        Field(
            None,
            description="For calculated project cards, must refer to the object to perform the calculation on. ",
        ),
    ]
    notes: Optional[str] = None


class ProjectCardModel8(BaseModel):
    field_schema: Annotated[
        Optional[str],
        Field(
            None,
            alias="$schema",
            description="Reference to the project card schema which this file uses. If not specified, will be assumed to be the most recent release.",
        ),
    ]
    project: Annotated[
        str, Field(description="A project name which uniquely identifies this project")
    ]
    dependencies: Optional[Dependencies] = None
    tags: Optional[Tags] = None
    roadway_deletion: Optional[ChangeRoadwayDeletion] = None
    roadway_addition: Optional[ChangeRoadwayAddition] = None
    roadway_property_change: Optional[ChangeRoadwayPropertyChange] = None
    roadway_managed_lanes: Optional[ChangeRoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None
    changes: List[Change]
    self_obj_type: Annotated[
        Optional[SelfObjType],
        Field(
            None,
            description="For calculated project cards, must refer to the object to perform the calculation on. ",
        ),
    ]
    notes: Optional[str] = None


class ProjectCardModel(
    RootModel[
        Union[
            ProjectCardModel1,
            ProjectCardModel2,
            ProjectCardModel3,
            ProjectCardModel4,
            ProjectCardModel5,
            ProjectCardModel6,
            ProjectCardModel7,
            ProjectCardModel8,
        ]
    ]
):
    root: Annotated[
        Union[
            ProjectCardModel1,
            ProjectCardModel2,
            ProjectCardModel3,
            ProjectCardModel4,
            ProjectCardModel5,
            ProjectCardModel6,
            ProjectCardModel7,
            ProjectCardModel8,
        ],
        Field(title="Project Card Schema"),
    ]
