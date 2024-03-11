from __future__ import annotations
from typing import Any, Annotated, Dict, List, Optional, Union
from pydantic import ConfigDict, Field

from ..._base.models import Timespan, RecordModel
from ...gtfs.models import *
from ...roadway.models import *

from .types import *


class GroupItem(RecordModel):
    """Value for setting property value for a group category."""

    model_config = ConfigDict(extra='forbid')

    category: List[str]
    value: Annotated[float, Field(ge=0.0)]
    _examples = [{'category': ['hov3', 'hov2'], 'value': 2.0}]


class ByAccessCategory(RecordModel):
    """Setting a property value for a group category."""

    model_config = ConfigDict(extra='forbid')

    default: Annotated[float, Field(ge=0.0)]
    group: Optional[List[GroupItem]] = None
    _examples = [
        {
            'default': 0,
            'group': [
                {'category': ['hov3', 'hov2'], 'value': 2.0},
                {'category': ['truck'], 'value': 4.0},
            ],
        }
    ]


class TimeofdayCategoryItem(RecordModel):
    """Value for setting property value for a time of day and category"""

    model_config = ConfigDict(extra='forbid')

    category: List[str]
    timespan: Timespan
    value: Annotated[float, Field(ge=0.0)]
    _examples = [{'category': ['hov3', 'hov2'], 'timespan': ['6:00', '9:00'], 'value': 2.0}]


class ByAccessCategoryAndTimeOfDay(RecordModel):
    """Setting a property value for a time of day and group category."""

    model_config = ConfigDict(extra='forbid')

    default: Annotated[float, Field(ge=0.0)]
    timeofday: List[TimeofdayCategoryItem]
    _examples = [
        {
            'default': 0,
            'timeofday': [
                {'category': ['hov3', 'hov2'], 'timespan': ['6:00', '9:00'], 'value': 2.0},
                {'category': ['truck'], 'timespan': ['6:00', '9:00'], 'value': 4.0},
            ],
        }
    ]


class TimeofdayItem(RecordModel):
    """Value for setting property value for a time of day."""

    model_config = ConfigDict(extra='forbid')

    timespan: Timespan
    value: Annotated[float, Field(ge=0.0)]
    _examples = [{'timespan': ['6:00', '9:00'], 'value': 2.0}]


class ByTimeOfDay(RecordModel):
    """Setting a property value for a time of day."""

    model_config = ConfigDict(extra='forbid')

    default: Annotated[float, Field(ge=0.0)]
    timeofday: List[TimeofdayItem]
    _examples = [
        {
            'default': 0,
            'timeofday': [
                {'timespan': ['6:00', '9:00'], 'value': 2.0},
                {'timespan': ['9:00', '15:00'], 'value': 4.0},
            ],
        }
    ]


class Dependencies(RecordModel):
    """Project dependencies."""

    model_config = ConfigDict(extra='forbid')

    prerequisites: Optional[Prerequisites]
    corequisites: Optional[Corequisites]
    conflicts: Optional[Conflicts]

    _examples = [
        {
            'prerequisites': ['7th St E Road Diet'],
            'corequisites': ['8th St E Road Diet'],
            'conflicts': ['9th St E Road Diet'],
        }
    ]


class SelectNode(RecordModel):
    """Selection of a single roadway node in the `facility` section of a project card."""

    model_config = ConfigDict(extra='forbid')

    osm_node_id: Optional[OsmNodeId] = None
    model_node_id: Optional[ModelNodeId] = None
    _examples = [{'osm_node_id': '12345'}, {'model_node_id': 67890}]


class PropertySet(RecordModel):
    """Set a property value for a facility."""

    require_one_of = ["set", "change"]
    model_config = ConfigDict(extra='forbid')

    existing: Optional[Union[float, str]] = None
    change: Optional[Union[float, str]] = None
    set: Optional[Union[float, str]] = None

    _examples = [{'existing': 1, 'change': 2}, {'set': 1}]


Routing = Annotated[
    List[int],
    Field(
        description='List of nodes that the trip traverses with a `-` in front of nodes where the service does not stop.'
    ),
]


class SelectRouteProperties(RecordModel):
    """Selection properties for transit routes."""

    model_config = ConfigDict(extra='allow')

    route_short_name: Annotated[Optional[List[RouteShortName]], Field(None, min_length=1)]
    route_long_name: Annotated[Optional[List[RouteLongName]], Field(None, min_length=1)]
    agency_id: Annotated[Optional[List[AgencyID]], Field(None, min_length=1)]
    route_type: Annotated[Optional[List[RouteType]], Field(None, min_length=1)]


class Routing(RecordModel):
    """Routing for transit trips."""

    model_config = ConfigDict(extra='forbid')

    existing: Optional[TransitRouting] = None
    set: TransitRouting
    _examples = [{'set': [1, 2, 3]}, {'existing': [1, 2, 3], 'change': [1, 2, 5, 3]}]


class SelectLinks(RecordModel):
    """
    requirements for describing links in the `facility` section of a project card.

    examples:

    ```python
        {'name': ['Main St'], 'modes': ['drive']}
        {'osm_link_id': ['123456789']}
        {'model_link_id': [123456789], 'modes': ['walk']}
        {'all': 'True', 'modes': ['transit']}
    ```

    """

    one_of = ["name", "ref", "osm_link_id", "model_link_id", "all"]
    model_config = ConfigDict(extra='allow')

    all: Optional[SelectAll] = None
    name: Annotated[Optional[List[ProjectName]], Field(None, min_length=1)]
    ref: Annotated[Optional[List[Ref]], Field(None, min_length=1)]
    osm_link_id: Annotated[Optional[List[OsmLinkId]], Field(None, min_length=1)]
    model_link_id: Annotated[Optional[List[ModelLinkId]], Field(None, min_length=1)]
    modes: Optional[List[Mode]] = None

    _examples = [
        {'name': ['Main St'], 'modes': ['drive']},
        {'osm_link_id': ['123456789']},
        {'model_link_id': [123456789], 'modes': ['walk']},
        {'all': 'True', 'modes': ['transit']},
    ]


class SelectNodes(RecordModel):
    """Requirements for describing multiple nodes of a project card (e.g. to delete)."""

    require_any_of = ["osm_node_id", "model_node_id"]
    model_config = ConfigDict(extra='forbid')

    osm_node_id: Annotated[Optional[List[OsmNodeId]], Field(None, min_length=1)]
    model_node_id: Annotated[List[ModelNodeId], Field(min_length=1)]

    _examples = [
        {'osm_node_id': ['12345', '67890'], 'model_node_id': [12345, 67890]},
        {'osm_node_id': ['12345', '67890']},
        {'model_node_id': [12345, 67890]},
    ]


class SelectTransitNodes(RecordModel):
    """Requirements for describing multiple transit nodes of a project card (e.g. to delete)."""

    require_any_of = [
        "osm_node_id",
        "model_node_id",
    ]
    model_config = ConfigDict(extra='forbid')

    stop_id: Annotated[Optional[List[StopID]], Field(None, min_length=1)]
    model_node_id: Annotated[List[ModelNodeId], Field(min_length=1)]
    require: Optional[SelectionRequire] = None

    _examples = [
        {'stop_id': ['stop1', 'stop2'], 'require': 'any'},
        {'model_node_id': [1, 2], 'require': 'all'},
    ]


PropertyChanges = Annotated[Dict[str, PropertySet], Field(min_length=1)]


class SelectSegment(RecordModel):
    """Roadway Facility Selection."""

    one_of = ["links", "nodes", ["links", "from", "to"]]
    model_config = ConfigDict(extra='forbid')

    links: Optional[SelectLinks] = None
    nodes: Optional[SelectNodes] = None
    from_: Annotated[Optional[SelectNode], Field(None, alias='from')]
    to: Optional[SelectNode] = None

    _examples = [
        {
            'links': {'name': ['Main Street']},
            'from': {'model_node_id': 1},
            'to': {'model_node_id': 2},
        },
        {'nodes': {'osm_node_id': ['1', '2', '3']}},
        {'nodes': {'model_node_id': [1, 2, 3]}},
        {'links': {'model_link_id': [1, 2, 3]}},
    ]


class SelectTripProperties(RecordModel):
    """Selection properties for transit trips."""

    model_config = ConfigDict(extra='allow')

    trip_id: Annotated[Optional[List[TripID]], Field(None, min_length=1)]
    shape_id: Annotated[Optional[List[ShapeID]], Field(None, min_length=1)]
    direction_id: Optional[DirectionID] = None
    service_id: Annotated[Optional[List[ServiceID]], Field(None, min_length=1)]
    route_id: Annotated[Optional[List[RouteID]], Field(None, min_length=1)]
    trip_short_name: Annotated[Optional[List[TripShortName]], Field(None, min_length=1)]


class RoadwayDeletionChange(RecordModel):
    """Change for deleting roadway links and/or nodes."""

    any_of = ["links", "nodes"]
    model_config = ConfigDict(extra='forbid')

    links: Optional[SelectLinks] = None
    nodes: Optional[SelectNodes] = None

    _examples = [
        {'links': {'model_link_id': [1, 2, 3]}},
        {'links': {'ref': ['I-5'], 'lanes': 2}},
        {'nodes': {'model_node_id': [1, 2, 3]}},
    ]


ScopedNumberPropertyValue = Union[ByTimeOfDay, ByAccessCategory, ByAccessCategoryAndTimeOfDay]


class RoadwayPropertyChange(RecordModel):
    model_config = ConfigDict(extra='forbid')
    facility: SelectSegment
    property_changes: PropertyChanges


class SelectTrips(RecordModel):
    model_config = ConfigDict(extra='forbid')
    trip_properties: Optional[SelectTripProperties] = None
    route_properties: Optional[SelectRouteProperties] = None
    timespans: Annotated[Optional[List[Timespan]], Field(None, min_length=1)]
    nodes: Optional[SelectNodes] = None


class TransitRoutingChange(RecordModel):
    """Change for transit routing."""

    model_config = ConfigDict(extra='forbid')

    service: SelectTrips
    routing: Routing
    _examples = [
        {
            'service': {'route_id': ['1', '2'], 'timespans': [['6:00', '9:00']]},
            'routing': {'set': [1, 2, 3]},
        },
        {'service': {'agency_id': ['A']}, 'routing': {'existing': [1, 2, 3], 'set': [1, 2, 5, 3]}},
    ]


class RoadwayAdditionChange(RecordModel):
    """Change for adding roadway links and/or nodes."""

    require_any_of = ["links", "nodes"]
    model_config = ConfigDict(extra='forbid')

    links: Optional[List[RoadwayLink]] = None
    nodes: Optional[List[RoadwayNode]] = None
    _examples = [
        {
            'links': [
                {
                    'A': 1,
                    'B': 2,
                    'model_link_id': 123,
                    'name': 'Elm Street',
                    'roadway': 'residential',
                    'lanes': 2,
                    'price': 0.75,
                    'walk_access': 1,
                    'bike_access': 1,
                    'bike_facility': 1,
                    'drive_access': 1,
                    'bus_only': 0,
                    'rail_only': 0,
                }
            ],
            'nodes': [
                {'model_node_id': 1, 'X': -122.419, 'Y': 37.7},
                {'model_node_id': 2, 'X': -122.419, 'Y': 37.8},
            ],
        }
    ]


class TransitPropertyChange(RecordModel):
    """Change for transit properties."""

    model_config = ConfigDict(extra='forbid')

    service: SelectTrips
    property_changes: Dict[str, PropertySet]
    _examples = [
        {
            'service': {'route_id': ['1', '2'], 'timespans': [['6:00', '9:00']]},
            'property_changes': {'headway': {'set': 10}},
        },
        {'service': {'agency_id': ['A']}, 'property_changes': {'headway': {'set': 10}}},
    ]


class Change(RecordModel):
    require_one_of = [
        "roadway_deletion",
        "roadway_addition",
        "roadway_property_change",
        "roadway_managed_lanes",
        "transit_property_change",
        "transit_routing_change",
    ]
    roadway_deletion: Optional[RoadwayDeletionChange] = None
    roadway_addition: Optional[RoadwayAdditionChange] = None
    roadway_property_change: Optional[RoadwayPropertyChange] = None
    roadway_managed_lanes: Optional[RoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None


class RecordModel(RecordModel):
    require_one_of = [
        "roadway_deletion",
        "roadway_addition",
        "roadway_property_change",
        "roadway_managed_lanes",
        "transit_property_change",
        "transit_routing_change",
        ["pycode", "self_obj_type"],
        "changes",
    ]

    project: ProjectName
    dependencies: Optional[Dependencies] = None
    tags: Optional[Tags] = None
    roadway_deletion: Optional[RoadwayDeletionChange] = None
    roadway_addition: Optional[RoadwayAdditionChange] = None
    roadway_property_change: Optional[RoadwayPropertyChange] = None
    roadway_managed_lanes: Optional[RoadwayPropertyChange] = None
    transit_property_change: Optional[TransitPropertyChange] = None
    transit_routing_change: Optional[TransitRoutingChange] = None
    pycode: Optional[Pycode] = None
    changes: Optional[List[Change]]
    self_obj_type: Optional[SelfObjType]
    notes: Optional[str] = None
