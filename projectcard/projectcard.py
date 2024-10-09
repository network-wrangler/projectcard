"""Project Card class for project card data schema."""

from __future__ import annotations

from typing import Union

from .errors import ProjectCardValidationError, SubprojectValidationError
from .logger import CardLogger
from .utils import _findkeys
from .validate import (
    update_dict_with_schema_defaults,
    validate_card,
)

UNSPECIFIED_PROJECT_NAMES = ["", "TO DO User Define", "USER TO define"]
VALID_EXT = [".yml", ".yaml", ".json", ".toml", ".wr", ".wrangler"]
REPLACE_KEYS = {"a": "A", "b": "B"}
CHANGE_TYPES = [
    "roadway_property_change",
    "roadway_addition",
    "roadway_deletion",
    "transit_property_change",
    "transit_routing_change",
    "transit_service_deletion",
    "transit_route_addition",
    "pycode",
]


class ProjectCard:
    """Representation of a Project Card.

    Attributes:
        __dict__: Dictionary of project card attributes
        project: Name of project
        dependencies: Dependencies of project
        tags: Tags of project
        notes: Notes about project
        valid: Boolean indicating if data conforms to project card data schema
        facilities: List of all facility objects in project card
        facility: either singular facility in project card or the string "multiple"
        all_property_changes: List of all property_changes objects in project card
        property_changes: either singular property_changes in project card or the string "multiple"
        change_types: List of all project types in project card
        change_type: either singular project type in project card or the string "multiple"
        sub_projects: list of sub_project objects
    """

    def __init__(self, attribute_dictonary: dict, use_defaults: bool = True):
        """Constructor for ProjectCard object.

        Args:
            attribute_dictonary: a nested dictionary of attributes
            use_defaults: if True, will use default values for missing required attributes,
                if exist in schema. Defaults to True.
        """
        # add these first so they are first on write out
        self.tags: list[str] = []
        self.dependencies: dict = {}
        self.notes: str = ""
        self._sub_projects: list[SubProject] = []
        if use_defaults:
            attribute_dictonary = update_dict_with_schema_defaults(attribute_dictonary)
        self.__dict__.update(attribute_dictonary)
        for sp in self.__dict__.get("changes", []):
            sp_obj = SubProject(sp, self)
            self._sub_projects.append(sp_obj)

    def __str__(self):
        """String representation of project card."""
        s = [f"{key}: {value}" for key, value in self.__dict__.items()]
        return "\n".join(s)

    def validate(self) -> bool:
        """Return True if project card is valid, False otherwise."""
        return validate_card(self.__dict__)

    @property
    def to_dict(self) -> dict:
        """Return dictionary of public project card attributes."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_") and v is not None}

    @property
    def valid(self) -> bool:
        """Return True if project card is valid, False otherwise."""
        try:
            self.validate()
        except ProjectCardValidationError as e:
            CardLogger.error(f"Project {self.project} is not valid: {e}")
            return False
        return True

    @property
    def facilities(self) -> list[dict]:
        """Return all facilities from project card as list of dicts."""
        if any("transit" in t for t in self.change_types):
            CardLogger.warning("Transit project doesn't have services.")
            return []
        f = list(_findkeys(self.__dict__, "facility"))
        if not f:
            msg = f"Couldn't find facility in project card {self.project}"
            raise ProjectCardValidationError(msg)
        return f

    @property
    def facility(self) -> Union[str, dict]:
        """Return facility part of project card or "multiple" if more than one."""
        f = self.facilities
        if len(f) > 1:
            return "multiple"
        return f[0]

    @property
    def services(self) -> list[dict]:
        """Return all services from project card as list of dicts."""
        if any("roadway" in t for t in self.change_types):
            CardLogger.warning("Roadway project doesn't have services.")
            return []
        s = list(_findkeys(self.__dict__, "service"))
        if not s:
            msg = f"Couldn't find service in project card {self.project}"
            raise ProjectCardValidationError(msg)
        return s

    @property
    def service(self) -> Union[str, dict]:
        """Return service part of from project card or "multiple" if more than one."""
        s = self.services
        if len(s) > 1:
            return "multiple"
        return s[0]

    @property
    def all_transit_property_changes(self) -> list[dict]:
        """Return all transit property changes from project card."""
        if not any("transit_property_change" in t for t in self.change_types):
            CardLogger.warning(f"Project {self.project} doesn't have transit property changes.")
            return []
        tp = list(_findkeys(self.__dict__, "transit_property_change"))
        p = [i["property_changes"] for i in tp]
        return p

    @property
    def transit_property_change(self) -> Union[str, dict]:
        """Return transit property change from project card or "multiple if more than one."""
        p = self.all_transit_property_changes
        if len(p) > 1:
            return "multiple"
        return p[0]

    @property
    def all_transit_routing_changes(self) -> list[dict]:
        """Return all transit routing changes from project card."""
        if not any("transit_routing_change" in t for t in self.change_types):
            CardLogger.warning(f"Project {self.project} doesn't have routing changes.")
            return []
        r = list(_findkeys(self.__dict__, "routing"))
        CardLogger.debug(f"transit routing change: {r}")
        return r

    @property
    def transit_routing_change(self) -> Union[str, dict]:
        """Return transit routing change from project card."""
        p = self.all_transit_routing_changes
        if len(p) > 1:
            return "multiple"
        return p[0]

    @property
    def change_types(self) -> list[str]:
        """Returns list of all change types from project/subproject."""
        if self._sub_projects:
            return [sp.change_type for sp in self._sub_projects]

        type_keys = [k for k in self.__dict__ if k in CHANGE_TYPES]
        if not type_keys:
            msg = f"Couldn't find type of project card {self.project}"
            raise ProjectCardValidationError(msg)
        return type_keys

    @property
    def change_type(self) -> str:
        """Return single change type if single project or "multiple" if >1 subproject."""
        t = self.change_types
        if len(t) > 1:
            return "multiple"
        return t[0]


class SubProject:
    """Representation of a SubProject within a ProjectCard.

    Attributes:
        parent_project: reference to parent ProjectCard object
        type:  project type
        tags: reference to parent project card tags
        dependencies: reference to parent project card's dependencies
        project: reference to the name of the parent project card's name
        facility: facility selection dictionary
        property_changes:property_changes dictionary
    """

    def __init__(self, sp_dictionary: dict, parent_project: ProjectCard):
        """Constructor for SubProject object.

        Args:
            sp_dictionary (dict): dictionary of sub-project attributes contained within "changes"
                list of parent projet card
            parent_project (ProjectCard): ProjectCard object for parent project card

        """
        self._parent_project = parent_project

        if len(sp_dictionary) != 1:
            msg = f"Subproject of {parent_project.project} should only have one change. Found {len(sp_dictionary)} changes."
            CardLogger.error(
                msg
                + f"  Did you forget to indent the rest of this change?\nKeys: {sp_dictionary.keys()}"
            )
            raise SubprojectValidationError(msg)
        self._change_type = next(iter(sp_dictionary.keys()))
        self.__dict__.update(sp_dictionary)
        self._sub_projects: list[SubProject] = []

    @property
    def change_type(self) -> str:
        """Return change type from subproject."""
        return self._change_type

    @property
    def parent_project(self) -> ProjectCard:
        """Return parent project from parent project card."""
        return self._parent_project

    @property
    def project(self) -> str:
        """Return project name from parent project card."""
        return self._parent_project.project

    @property
    def dependencies(self) -> dict:
        """Return dependencies from parent project card."""
        return self._parent_project.dependencies

    @property
    def tags(self) -> list[str]:
        """Return tags from parent project card."""
        return self._parent_project.tags

    @property
    def facility(self) -> dict:
        """Return facility dictionary from subproject."""
        f = list(_findkeys(self.__dict__, "facility"))
        if not f:
            msg = f"Couldn't find facility in subproject in project card {self._parent_project.project}"
            raise SubprojectValidationError(msg)
        return f[0]

    @property
    def valid(self) -> bool:
        """Check if subproject is valid."""
        return self._parent_project.valid
