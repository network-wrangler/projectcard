from typing import Optional

from .tables import *
from ..._base.models import DBModel
from ..._base.models import RecordModel


class GTFSModel(RecordModel, DBModel):
    """Requirements for gtfs network."""

    stops: StopsTable
    routes: RoutesTable
    trips: TripsTable
    stop_times: StopTimesTable
    shapes: Optional[ShapesTable] = None
    frequencies: Optional[FrequenciesTable] = None
    agencies: Optional[AgenciesTable] = None
