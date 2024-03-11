from enum import Enum
from typing import List, Annotated, Optional, Union, Literal, Any

from pydantic import Field, BeforeValidator, NonNegativeFloat, ScopedNumberPropertyValue

ProjectName = Annotated[
    str,
    Field(
        ...,
        title='Project Name',
        description='A project name which uniquely identifies this project',
    ),
]

Prerequisites = Annotated[
    List[ProjectName], Field([], examples=['7th St E Road Diet'], title='Project Prerequisites')
]
Corequisites = Annotated[
    List[ProjectName], Field([], examples=['7th St E Road Diet'], title='Project Co-requisites')
]
Conflicts = Annotated[
    List[ProjectName], Field([], examples=['7th St E Road Diet'], title='Project Conflicts')
]

TransitRouteNode = Annotated[int, Field(title='Transit Route Node')]

TransitRouting = Annotated[List[TransitRouteNode], Field(title='Transit Routing Changes')]


class SelectionRequire(Enum):
    """Indicator if any or all is required."""

    any = 'any'
    all = 'all'


Tag = Annotated[str, BeforeValidator(str), Field(examples=['vision2050'])]
Pycode = Annotated[str, "Python code to be executed."]

Tags = Annotated[List[Tag], Field(title='Project Tags')]


class SelectAll(Enum):
    True_ = 'True'
    False_ = 'False'


class Mode(Enum):
    drive = 'drive'
    walk = 'walk'
    bike = 'bike'
    transit = 'transit'
    any = 'any'


class SelfObjType(Enum):
    """
    For calculated project cards, must refer to the object to perform the calculation on.
    """

    RoadwayNetwork = 'RoadwayNetwork'
    TransitNetwork = 'TransitNetwork'
