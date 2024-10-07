"""Field types for the projectcard models."""

from typing import Annotated, Literal, Union

from pydantic import Field

PositiveInt = Annotated[int, Field(gt=0)]

OsmRoadwayType = Literal[
    "taz",
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiary",
    "unclassified",
    "residential",
    "motorway_link",
    "trunk_link",
    "primary_link",
    "secondary_link",
    "tertiary_link",
    "living_street",
    "service",
    "pedestrian",
    "footway",
    "steps",
    "cycleway",
    "track",
    "bus_guideway",
    "road",
]
"""Open Street Map Roadway Types. See: <https://wiki.openstreetmap.org/wiki/Key:highway>."""


MLAccessEgress = Union[Literal["all"], list[int]]
"""Determines how managed lanes can be accessed from the general purpose lanes as represented
by connector links. If `all` is specied, all managed lanes will be able to access managed lanes.
Otherwise, a list of node IDs where access is allowed is provided. If nothing is specified for
a continuous managed lane, access is assumed to be allowed at all nodes."""

Mode = Literal["drive", "walk", "bike", "transit", "any"]
"""Which modes are searched for. If `any` is specified, all modes are searched for."""

Longitude = Annotated[float, Field(ge=-180.0, le=180.0)]
Latitude = Annotated[float, Field(ge=-90.0, le=90.0)]


TimeString = Annotated[
    str,
    Field(
        description="A time string in the format HH:MM or HH:MM:SS",
        pattern=r"^(\d+):([0-5]\d)(:[0-5]\d)?$",
    ),
]
"""A HH:MM or HH:MM:SS time string. Example: `"23:44"`."""

Timespan = Annotated[
    list[TimeString], Field(examples=[["12:00", "19:45:00"]], max_length=2, min_length=2)
]
"""A list of two time strings representing a start and end time for a time span.
Example: `["12:00", "19:45:00"]`."""
