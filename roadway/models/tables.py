from typing import Optional


import pandera as pa
from pandera import DataFrameModel, Field, Series, GeoSeries

from .types import *


class RoadwayNodesTable(DataFrameModel):
    """Datamodel used to validate if nodes table is of correct format and types."""

    model_node_id: Series[int] = Field(coerce=True, unique=True, nullable=False)

    geometry: GeoSeries
    X: Series[X] = Field(coerce=True, nullable=False)
    Y: Series[Y] = Field(coerce=True, nullable=False)

    # optional fields
    Z: Optional[Series[Z]] = pa.Field(coerce=True, nullable=True)
    osm_node_id: Optional[Series[OsmNodeId]] = pa.Field(coerce=True, unique=True, nullable=True)

    class Config:
        coerce = True
        _pk = ["model_node_id"]
        _fk = {}


class RoadwayShapesTable(DataFrameModel):
    """Datamodel used to validate if shapes_df is of correct format and types."""

    shape_id: Series[RoadwayShapeId] = pa.Field(unique=True)
    geometry: GeoSeries = pa.Field()

    class Config:
        coerce = True
        _pk = ["shape_id"]
        _fk = {}


class RoadwayLinksTable(DataFrameModel):
    """Datamodel used to validate if links_df is of correct format and types."""

    model_link_id: Series[ModelLinkId] = pa.Field(coerce=True, unique=True)
    A: Series[ModelNodeId] = pa.Field(nullable=False)
    B: Series[ModelNodeId] = pa.Field(nullable=False)
    geometry: GeoSeries = pa.Field(nullable=False)
    name: Series[LinkName] = pa.Field(nullable=False)
    rail_only: Series[RailOnly] = pa.Field(coerce=True, nullable=False)
    bus_only: Series[BusOnly] = pa.Field(coerce=True, nullable=False)
    drive_access: Series[DriveAccess] = pa.Field(coerce=True, nullable=False)
    bike_access: Series[BikeAccess] = pa.Field(coerce=True, nullable=False)
    walk_access: Series[WalkAccess] = pa.Field(coerce=True, nullable=False)

    roadway: Series[RoadwayType] = pa.Field(nullable=False)
    lanes: Series[Lanes] = pa.Field(coerce=True, nullable=False)

    # Optional Fields
    truck_access: Optional[Series[TruckAccess]] = pa.Field(coerce=True, nullable=True)
    osm_link_id: Optional[Series[OsmLinkId]] = pa.Field(coerce=True, nullable=True)
    locationReferences: Optional[Series[LocationReferences]] = pa.Field(nullable=True)
    shape_id: Optional[Series[RoadwayShapeId]] = pa.Field(nullable=True)

    class Config:
        coerce = True
        _pk = ["model_link_id"]
        _fk = {
            "A": {"table": "nodes", "field": "model_node_id"},
            "B": {"table": "nodes", "field": "model_node_id"},
            "shape_id": {"table": "shapes", "field": "shape_id"},
        }
        uniqueness = ["A", "B"]
