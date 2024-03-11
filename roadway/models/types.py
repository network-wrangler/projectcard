from enum import Enum
from typing import Annotated, Any, Literal, List, Optional, Union

from pydantic import Field, BaseModel, NonNegativeFloat, ScopedNumberPropertyValue

Bearing = Annotated[
    int,
    Field(
        None,
        description='The angle of the eminating arc from the point, expressed in clockwise degrees from North (0)',
        examples=[0, 90, 275],
        ge=0,
        le=360,
    ),
]
BikeAccess = Annotated[
    bool,
    Field(
        True,
        coerce=True,
        description='Indicates if a facility is generally available for cyclists. \
        Must not be true if any of bus_only or rail_only are true.',
    ),
]
BikeFacility = Enum[
    'BikeFacility',
    {
        'none': 0,
        'shared_use_path': 1,
        'bike_lane': 2,
        'bike_route': 3,
        'bike_blvd': 4,
        'bike_sharrow': 5,
        'bike_other': 6,
        'bike_facility': 7,
    },
]
BusOnly = Annotated[
    bool,
    Field(
        False,
        coerce=True,
        description='Indicates if a facility is rail-only if True.  \
    Must not be true if any of walk_access, bike_access, drive_access, rail_only are True.',
    ),
]
Distance = Annotated[float, Field(..., examples=[93.08], ge=0.0, title='Distance')]
DriveAccess = Annotated[
    bool,
    Field(
        True,
        coerce=True,
        description='Indicates if a facility is generally available for driving. \
        Must not be true if any of bus_only or rail_only are true.',
    ),
]
IntersectionId = Annotated[
    str,
    Field(
        '', description='The Intersectionid Schema', examples=['4d0231aa0ebb779f142c2518703ee481']
    ),
]
Lanes = Annotated[
    Union[NonNegativeFloat, ScopedNumberPropertyValue],
    Field(
        ...,
        description='Number of lanes either in simple or complex terms.',
        examples=[
            2,
            5,
            {'default': 1, 'timeofday': {'timespan': ['6:00', '9:00'], 'value': 2}},
        ],
    ),
]
LocationReferencePoint = Annotated[
    List[float], Field(None, description='Point of reference in X,Y,Z')
]
LocationReferences = Annotated[List[Any], Field(None, description='The Locationreferences Schema')]
MLAccessEgress = Annotated[
    Union[Literal['all'], List[Any]],
    Field(
        'all',
        description='Indicates where a managed lane facility can by accessed or \
                exited either by indicating `all` for everywhere, or listing foreign keys to specific A-nodes.',
        examples=['all', [123, 5543]],
    ),
]
ModelLinkId = Annotated[int, Field(..., description='Unique id for facility.')]
ModelNodeId = Annotated[int, Field(..., ge=0, description='Primary key to the nodes object.')]
LinkName = Annotated[
    str,
    Field(
        ...,
        description='Name of Roadway facility. If multiple, can be contatenated with a comma.',
        examples=[
            'Elm Street',
            'Raleigh Beltline',
            'Capital Beltway',
            '3rd St,Willie Mays Blvd',
        ],
    ),
]
OsmLinkId = Annotated[
    str,
    Field(
        '',
        description='Reference to the corresponding Open Street Map link. Note that due to link splitting this may or may not be unique, and is not a required attribute.',
    ),
]
OsmNodeId = Annotated[
    str,
    Field(
        '',
        description='Reference to the corresponding Open Street Map node.',
        examples=['954734870'],
    ),
]
Price = Annotated[
    Union[float, ScopedNumberPropertyValue],
    Field(
        0,
        description='Price of facility, either as a positive number of a complex type by time of day and/or access category.',
        examples=[
            0.75,
            2.9,
            {'default': 1, 'timeofday': {'time': ['6:00', '9:00'], 'value': 2}},
        ],
    ),
]
RailOnly = Annotated[
    bool,
    Field(
        False,
        coerce=True,
        description='Indicates if a facility is rail-only if True.  \
        Must not be true if any of walk_access, bike_access, drive_access, bus_only are True.',
    ),
]
Ref = Annotated[
    str,
    Field(
        '',
        description='Reference name of roadway, per Open Street Map definition.',
        examples=['I-40', 'US66', 'WA520'],
    ),
]
SegmentId = Annotated[
    Union[str, int],
    Field(
        None,
        description='An identifier for segments of roadway. Can be useful for querying and \
        setting values for parts of facilities, summary scripts, etc.',
    ),
]
RoadwayShapeId = Annotated[
    str,
    Field(
        ...,
        description='Unique id for roadway shape',
        examples=['6a22969708104ae2497244f3d079381d'],
    ),
]
ShstGeometryId = Annotated[
    str,
    Field(
        '', description='The Shstgeometryid Schema', examples=['6a22969708104ae2497244f3d079381d']
    ),
]
ShstReferenceIdLink = Annotated[
    str,
    Field(
        '', description='The Shstreferenceid Schema', examples=['6a22969708104ae2497244f3d079381d']
    ),
]
ShstReferenceIdNode = Annotated[
    str,
    Field(
        '',
        description='Shared streets node ID reference.',
        examples=['0751f5ce12472360fed0d0e80ceae35c'],
    ),
]
TruckAccess = Annotated[
    bool,
    Field(
        True, coerce=True, description='Indicates if a facility is generally available for Trucks.'
    ),
]
WalkAccess = Annotated[
    bool,
    Field(
        True,
        coerce=True,
        description='Indicates if a facility is generally available for pedestrians. \
        Must not be true if any of bus_only or rail_only are true.',
    ),
]
X = Annotated[float, Field(..., description='X coordinate (e.g. Longitude)')]
Y = Annotated[float, Field(..., description='Y coordinate (e.g. Latitude)')]
Z = Annotated[float, Field(None, description='Z coordinate (e.g. Altitude)')]


class BikeFacility(Enum):
    """
    Indicator for the category of bicycle facility on or along the roadway. If null, indicates unknown. If zero, indicates no facility.
    """

    none = 0
    shared_use_path = 1
    bike_lane = 2
    bike_route = 3
    bike_blvd = 4
    bike_sharrow = 5
    bike_other = 6
    bike_facility = 7


class LocationReference(BaseModel):
    sequence: Annotated[int, Field(ge=0)]
    point: List[LocationReferencePoint]
    distanceToNextRef: Optional[Distance] = None
    bearing: Optional[Bearing] = None
    intersectionId: Optional[IntersectionId] = None


class RoadwayType(Enum):
    """
    Roadway type, using [OSM Highway values](https://wiki.openstreetmap.org/wiki/Key:highway#Roads). Notes: * `X_link` roadway types denote linkage roads going to/from roadway type X (i.e. on/off ramps, etc). * `road` denotes unknown type.
    """

    motorway = 'motorway'
    trunk = 'trunk'
    primary = 'primary'
    secondary = 'secondary'
    tertiary = 'tertiary'
    unclassified = 'unclassified'
    residential = 'residential'
    motorway_link = 'motorway_link'
    trunk_link = 'trunk_link'
    primary_link = 'primary_link'
    secondary_link = 'secondary_link'
    tertiary_link = 'tertiary_link'
    living_street = 'living_street'
    service = 'service'
    pedestrian = 'pedestrian'
    footway = 'footway'
    steps = 'steps'
    cycleway = 'cycleway'
    track = 'track'
    bus_guideway = 'bus_guideway'
    road = 'road'
