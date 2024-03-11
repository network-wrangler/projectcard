from typing import Optional

from .tables import RoadwayNodesTable, RoadwayLinksTable, RoadwayShapesTable
from ..._base.models import DBModel
from ..._base.models import RecordModel


class RoadwayNetworkModel(RecordModel, DBModel):
    """
    Requirements for roadway network.
    """

    nodes: RoadwayLinksTable
    links: RoadwayNodesTable
    shapes: Optional[RoadwayShapesTable] = None
