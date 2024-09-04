from types import *
from records import *


class MockPaModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


try:
    from roadway import RoadwayNetworkModel
    from tables import RoadwayLinksTable, RoadwayNodesTable, RoadwayShapesTable
except ImportError:
    # Mock the data models
    import logging

    log = logging.getLogger(__name__)
    log.warning("Pandera is not installed, using mock models.")
    globals().update(
        {
            "RoadwayLinksTable": MockPaModel,
            "RoadwayNodesTable": MockPaModel,
            "RoadwayShapesTable": MockPaModel,
            "RoadwayNetworkModel": MockPaModel,
        }
    )
