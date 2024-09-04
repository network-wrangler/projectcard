"""This module defines the data models for various GTFS tables using pandera library.

The module includes the following classes:
- AgencyTable: Represents the Agency table in the GTFS dataset.
- StopsTable: Represents the Stops table in the GTFS dataset.
- RoutesTable: Represents the Routes table in the GTFS dataset.
- ShapesTable: Represents the Shapes table in the GTFS dataset.
- StopTimesTable: Represents the Stop Times table in the GTFS dataset.
- TripsTable: Represents the Trips table in the GTFS dataset.

Each table model leverages the Pydantic data models defined in the records module to define the
data model for the corresponding table. The classes also include additional configurations for,
such as uniqueness constraints.

There is NOT any foreign key validation in the data models.

Additionally, the module includes a custom check method called "uniqueness" that can be used to
check for uniqueness of values in a DataFrame.

For more examples of how to use Pandera DataModels, see the Pandera documentation at:
https://pandera.readthedocs.io/en/stable/dataframe-models.html

Usage examples:

1. Using a type decorator to automatically validate incoming table:

    ``` python
    import pandera as pa
    @pa.check_types
    def process_table(table: pa.DataFrameModel):
        # Perform operations on the table
        # The table will be automatically validated against its data model
        pass
    ```

2. Creating an instance of AgencyTable:

    ```python
    agency_table = AgencyTable(pd.from_csv("agency.csv")
    ```

2. Validating the StopsTable instance:

    ```python
    is_valid = stops_df.validate()
    ```

3. Checking uniqueness of values in a DataFrame:
    df = pd.DataFrame(...)  # DataFrame to check uniqueness
    is_unique = uniqueness(df, cols=["column1", "column2"])
"""

import pandera as pa
from pandera.engines.pandas_engine import PydanticModel

from ..._base.models.tables import *

from records import (
    AgencyRecord,
    FrequencyRecord,
    RouteRecord,
    ShapeRecord,
    StopRecord,
    StopTimeRecord,
    TripRecord,
)


class AgenciesTable(pa.DataFrameModel):
    """Represents the Agency table in the GTFS dataset.

    Configurations:
    - dtype: PydanticModel(AgencyRecord)
    - uniqueness: ["agency_id"]
    """

    class Config:
        dtype = PydanticModel(AgencyRecord)
        coerce = True
        _pk = ["agency_id"]
        _fk = {}
        uniqueness = ["agency_id"]


class StopsTable(pa.DataFrameModel):
    """Represents the Stops table in the GTFS dataset.

    Configurations:
    - dtype: PydanticModel(StopRecord)
    - uniqueness: ["stop_id"]
    """

    class Config:
        dtype = PydanticModel(StopRecord)
        coerce = True
        _pk = ["stop_id"]
        _fk = {}
        uniqueness = _pk


class RoutesTable(pa.DataFrameModel):
    """Represents the Routes table in the GTFS dataset.

    Configurations:
    - dtype: PydanticModel(RouteRecord)
    - uniqueness: ["route_id"]
    """

    class Config:
        dtype = PydanticModel(RouteRecord)
        coerce = True
        _pk = ["route_id"]
        _fk = {"agency_id": ["agencies", "agency_id"]}
        uniqueness = _pk


class ShapesTable(pa.DataFrameModel):
    """Represents the Shapes table in the GTFS dataset.

    Configurations:
    - dtype: PydanticModel(ShapeRecord)
    - uniqueness: ["shape_id", "shape_pt_sequence"]
    """

    class Config:
        dtype = PydanticModel(ShapeRecord)
        coerce = True
        _pk = ["shape_id", "shape_pt_sequence"]
        _fk = {"shape_id": ["routes", "field"]}
        uniqueness = _pk


class TripsTable(pa.DataFrameModel):
    """Represents the Trips table in the GTFS dataset.

    Configurations:
    - dtype: PydanticModel(TripRecord)
    """

    class Config:
        dtype = PydanticModel(TripRecord)
        coerce = True
        _fk = {"route_id": ["routes", "field"]}


class FrequenciesTable(pa.DataFrameModel):
    """Represents the Agency table in the GTFS dataset.

    Configurations:
    - dtype: PydanticModel(FrequencyRecord)
    - uniqueness: "trip_id","start_time"]
    """

    class Config:
        dtype = PydanticModel(FrequencyRecord)
        coerce = True
        _pk = ["trip_id", "start_time"]
        _fk = {"trip_id": ["routes", "trip_id"]}
        uniqueness = _pk


class StopTimesTable(pa.DataFrameModel):
    """Represents the Stop Times table in the GTFS dataset.

    Configurations:
    - dtype: PydanticModel(StopTimeRecord)
    - uniqueness: ["trip_id", "stop_sequence"]
    """

    class Config:
        dtype = PydanticModel(StopTimeRecord)
        coerce = True
        uniqueness = ["trip_id", "stop_sequence"]
        _fk = {
            "trip_id": ["trips", "trip_id"],
            "stop_id": ["stops", "stop_id"],
        }
