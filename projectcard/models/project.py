"""The project card data model."""

from typing import ClassVar, Literal, Optional

from changes import (
    ChangeTypes,
    RoadwayAddition,
    RoadwayDeletion,
    RoadwayPropertyChanges,
    TransitPropertyChange,
    TransitRouteAddition,
    TransitRoutingChange,
    TransitServiceDeletion,
)
from pydantic import BaseModel
from structs import Dependencies


class ProjectModel(BaseModel):
    """ProjectCard Data Model.

    ProjectCards are a set of information that describe an infrastructure project or change to a
    network. They are used to document and manage changes to a network such as adding a new bus
    route, changing a roadway property, changing the number of lanes on a roadway, or increasing
    transit service frequency.

    ProjectCards are composed of one or more **changes**. Each change is a specific type of change
    that happens to a specific portion, or **selection** of the network, such as a roadway
    property change, transit property change, or transit route addition. Each change type has
    its own set of parameters that describe the change in detail.

    #### Grouping Related Changes:
    When more than one change is needed to describe a project, the `changes` field can be used to
    specify a list of changes. This is useful when a project requires multiple changes to be made
    to the network. For example, a project to add a new bus route may require adding new bus lanes
    to the roadway network.  Or adding a new, mid-block bus-route may require adding a new bus stop
    as a node in the roadway network and splitting the link.

    While the user can choose what changes should be grouped together into a single,
    "project", they should be careful to ensure that the changes are logically related and would
    likely be implemented together.

    #### Phased Projects:
    In cases where a project maybe implemented in multiple phases, it is recommended to create
    separate project cards for each phase. This will help to ensure that the project can be
    in a network similar to how it would be implemented in the real world.

    #### Dependencies:
    If a project requires another project to be implemented first, the `pre-requisites` field
    of `dependencies` can be used.  Similarly, if a project would be impossible to implement
    if another project is implemented, the `conflicts` field of `dependencies` can be used.
    `corequisites` can be used to specify projects that must be implemented at the same time -
    noting that if Project A specifies Project B as a corequisite, then Project B need not specify
    Project A as a corequisite (if they were dependent upon each other, then they should likely
    be combined into a single project).

    #### Tags:
    Tags can be used to categorize projects and make it easier to search for projects that are
    related to a specific topic or type of project. For example, a collection of projects that are
    considered to be in your committed future baseline because they have committed funding could
    be tagged as `committed`.

    #### Formats + Serialization:
    ProjectCards can be represented within memory as any structured data format such as JSON,
    Python Dictionaries, or a Struct. They can also be serialized to any nested file format that
    is compatible with [JSON-schema ](https://json-schema.org) such as YAML, TOML, or JSON.
    For the purposes of this documentation, we will use YAML as the serialization format for
    the examples becuase it is less verbose than JSON and python dictonaries and easier to read.

    List of tools that support json-schema: <https://json-schema.org/tools>

    Attributes:
        project (str): The name of the project. This name must be unique within a set of projects
            being managed or applied to a network.
        notes (Optional[str]): Additional freeform notes about the project.
        tags (Optional[list[str]]): Tags for the project to associate the project card with a
            specific project or type of project.
        dependencies (Optional[Dependencies]): Dependencies for the project card: conflicts,
            prerequisites, and corequisites...each of which is a list of project names.
        changes (Optional[list[ChangeTypes]]): List of one or more changes. Must either have
            `changes` or a single change type (e.g. `roadway_property_change`,
            `transit_property_change`, etc.). If `changes` is provided, cannot specify another
            change outside of changes.
        roadway_property_change (Optional[RoadwayPropertyChanges]): A single roadway property
            change. Cannot be used with `changes` or another change type.
        roadway_deletion (Optional[RoadwayDeletion]): A single roadway deletion change. Cannot
            be used with `changes` or another change type.
        roadway_addition (Optional[RoadwayAddition]): A single roadway addition change. Cannot
            be used with `changes` or another change type.
        transit_property_change (Optional[TransitPropertyChange]): A single Transit property
            change. Cannot be used with `changes` or another change type.
        transit_routing_change (Optional[TransitRoutingChange]): A single Transit routing change.
            Cannot be used with `changes` or another change type.
        transit_service_deletion (Optional[TransitServiceDeletion]): A single Transit service
            deletion change. Cannot be used with `changes` or another change type.
        transit_route_addition (Optional[TransitRouteAddition]): A single transit route addition
            change. Cannot be used with `changes` or another change type.
        pycode (Optional[str]): A single pycode type change which uses python code for the project
            which refers to self as a transit or roadway network. Cannot be used with `changes` or
            another change type.
        self_obj_type (Optional[Literal["RoadwayNetwork", "TransitNetwork"]]): Type of object
            being changed in the pycode python code. Must be either TransitNetwork or
            RoadwayNetwork. Cannot be used with `changes` or another change type.

    !!! Example "Example Project Card"
        ```yaml
        project: "Add new bus route"
        notes: "This project adds a new bus route to the network."
        tags: ["bus", "transit"]
        dependencies:
            conflicts: ["Remove bus route"]
            prerequisites: ["Add bus stop"]
            corequisites: ["Add bus route"]
        transit_route_addition: ...
        ```
    """

    require_one_of: ClassVar = [
        "roadway_property_change",
        "roadway_deletion",
        "roadway_addition",
        "transit_property_change",
        "transit_routing_change",
        "transit_service_deletion",
        "transit_route_addition",
        ["pycode", "self_obj_type"],
        "changes",
    ]

    project: str
    notes: Optional[str]
    tags: Optional[list[str]]
    dependencies: Optional[Dependencies]
    changes: Optional[list[ChangeTypes]]
    roadway_property_change: Optional[RoadwayPropertyChanges]
    roadway_deletion: Optional[RoadwayDeletion]
    roadway_addition: Optional[RoadwayAddition]
    transit_property_change: Optional[TransitPropertyChange]
    transit_routing_change: Optional[TransitRoutingChange]
    transit_service_deletion: Optional[TransitServiceDeletion]
    transit_route_addition: Optional[TransitRouteAddition]
    pycode: Optional[str]
    self_obj_type: Optional[Literal["RoadwayNetwork", "TransitNetwork"]]
