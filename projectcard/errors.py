"""Custom errors for projectcard package."""
from jsonschema.exceptions import SchemaError, ValidationError


class ProjectCardReadError(Exception):
    """Error in reading project card."""
    

class ProjectCardValidationError(ValidationError):
    """Error in formatting of ProjectCard."""


class SubprojectValidationError(ProjectCardValidationError):
    """Error in formatting of Subproject."""


class PycodeError(ProjectCardValidationError):
    """Basic runtime error in python code."""


class ProjectCardJSONSchemaError(SchemaError):
    """Error in the ProjectCard json schema."""