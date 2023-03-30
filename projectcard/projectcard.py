from .validate import validate_card

UNSPECIFIED_PROJECT_NAMES = ["", "TO DO User Define", "USER TO define"]
VALID_EXT = [".yml", ".yaml", ".json", ".toml", ".wr", ".wrangler"]
REPLACE_KEYS = {"a": "A", "b": "B"}


class ProjectCard(object):
    """
    Representation of a Project Card

    Attributes:
        __dict__: Dictionary of project card attributes
        valid: Boolean indicating if data conforms to project card data schema
    """

    def __init__(self, attribute_dictonary: dict):
        """
        Constructor

        args:
            attribute_dictonary: a nested dictionary of attributes
        """
        # add these first so they are first on write out
        self.project = None
        self.tags = []
        self.dependencies = {}

        self.__dict__.update(attribute_dictonary)

    def __str__(self):
        s = ["{}: {}".format(key, value) for key, value in self.__dict__.items()]
        return "\n".join(s)

    @property
    def valid(self) -> bool:
        return validate_card(self.__dict__)
