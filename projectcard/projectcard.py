from typing import Union, List

from .logger import CardLogger
from .validate import validate_card
from .utils import findkeys

UNSPECIFIED_PROJECT_NAMES = ["", "TO DO User Define", "USER TO define"]
VALID_EXT = [".yml", ".yaml", ".json", ".toml", ".wr", ".wrangler"]
REPLACE_KEYS = {"a": "A", "b": "B"}



class ProjectCard(object):
    """
    Representation of a Project Card

    Attributes:
        __dict__: Dictionary of project card attributes
        valid: Boolean indicating if data conforms to project card data schema
        facilities: List of all facility objects in project card
        facility: either singular facility in project card or the string "multiple"  
        all_property_changes: List of all property_changes objects in project card
        property_changes: either singular property_changes in project card or the string "multiple"  
        types: List of all project types in project card
        type: either singular project type in project card or the string "multiple"  
        sub_projects: list of sub_project objects
    """

    def __init__(self, attribute_dictonary: dict):
        """
        Constructor

        args:
            attribute_dictonary: a nested dictionary of attributes
        """
        # add these first so they are first on write out
        self.project: str = None
        self.tags: list[str] = []
        self.dependencies: dict = {}
        self.sub_projects: list[SubProject] = []

        self.__dict__.update(attribute_dictonary)
        for sp in self.__dict__.get("changes",[]):
            sp_obj = SubProject(sp, self)
            self.sub_projects.append(sp_obj)

    def __str__(self):
        s = ["{}: {}".format(key, value) for key, value in self.__dict__.items()]
        return "\n".join(s)

    @property
    def valid(self) -> bool:
        return validate_card(self.__dict__)

    @property
    def facilities(self) -> List[dict]:
        if not any(["transit" in t for t in self.types]):
            CardLogger.warning("Transit project doesn't have services.")
            return []
        f = list(findkeys(self.__dict__,"facility"))
        if not f:
            raise ValueError("Couldn't find facility in project card")
        return f
    
    @property
    def facility(self) -> Union[str,dict]:
        f = self.facilities
        if len(f) > 1:
            return "multiple"
        return f[0]

    @property
    def services(self) -> List[dict]:
        if not any(["roadway" in t for t in self.types]):
            CardLogger.warning("Roadway project doesn't have services.")
            return []
        f = list(findkeys(self.__dict__,"service"))
        if not f:
            raise ValueError("Couldn't find service in project card")
        return f
    
    @property
    def service(self) -> Union[str,dict]:
        f = self.services
        if len(f) > 1:
            return "multiple"
        return f[0]
    
    @property
    def all_property_changes(self) -> List[dict]:
        p = list(findkeys(self.__dict__,"property_changes"))
        return p

    @property
    def property_changes(self) -> Union[str,dict]:
        p = self.all_property_changes
        if len(p) > 1:
            return "multiple"
        return p[0]
    
    @property
    def types(self) -> List[str]:
        if self.sub_projects:
            return [sp.type for sp in self.sub_projects]
        _ignore = ["project","tags","notes","dependencies","self","pycode","sub_projects","file"]
        type_keys = [k for k in self.__dict__.keys() if k not in _ignore]
        if not type_keys:
            raise ValueError("Couldn't find type of project card")
        return type_keys
    
    @property
    def type(self) -> str:
        t = self.types
        if len(t)>1:
            return "multiple"
        return t[0]


class SubProject(ProjectCard):
    """
    Representation of a SubProject within a ProjectCard

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
        self.parent_project = parent_project

        assert len(sp_dictionary) == 1
        self._type = list(sp_dictionary.keys())[0]
        self.__dict__.update(sp_dictionary[self.type])
        self.sub_projects = []

    @property
    def type(self) -> str:
        # have to override as a method because is a method in super class
        return self._type
    
    @property
    def project(self) -> str:
        return self.parent_project.project

    @property
    def dependencies(self) -> str:
        return self.parent_project.dependencies
    
    @property
    def tags(self) -> str:
        return self.parent_project.tags
    
    @property
    def property_changes(self) -> dict:
        f = self.__dict__.get("property_changes",{})
        return f
    
    @property
    def facility(self) -> dict:
        f = self.__dict__.get("facility",{})
        return f

    @property
    def valid(self) -> bool:
        return self.parent_project.valid