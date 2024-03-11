from typing import Optional

from ..._base.models import RecordModel
from .types import *


class RoadwayNode(RecordModel):
    """
    Requirements for roadway nodes.
    """

    model_node_id: ModelNodeId
    osm_node_id: Optional[OsmNodeId] = None
    shstReferenceId: Optional[ShstReferenceIdNode] = None
    outboundReferenceIds: Optional[List[ShstReferenceIdLink]] = None
    inboundReferenceIds: Optional[List[ShstReferenceIdLink]] = None
    X: X
    Y: Y
    Z: Optional[Z] = None


class RoadwayLink(RecordModel):
    """
    Requirements for roadway links.
    """

    A: ModelNodeId
    B: ModelNodeId
    model_link_id: ModelLinkId
    name: LinkName
    roadway: RoadwayType
    lanes: Lanes
    walk_access: WalkAccess
    bike_access: BikeAccess
    bus_only: BusOnly
    rail_only: RailOnly
    drive_access: DriveAccess
    osm_link_id: Optional[OsmLinkId] = None
    shstReferenceId: Optional[ShstReferenceIdLink] = None
    shstGeometryId: Optional[ShstGeometryId] = None
    locationReferences: Optional[LocationReferences] = None
    ref: Optional[Ref] = None
    price: Optional[Price] = None
    ML_lanes: Optional[Lanes] = None
    ML_price: Optional[Price] = None
    ML_access: Optional[MLAccessEgress] = None
    ML_egress: Optional[MLAccessEgress] = None
    bike_facility: Optional[BikeFacility] = None
    segment_id: Optional[SegmentId] = None
