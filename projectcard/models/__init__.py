"""Pydantic data models for the projectcard schema as a convenience product to use in Python tools.

Checks if pydantic is installed and imports data models. If pydantic is not installed, its
functionality will be "mocked" so that the project card package can be used without pydantic.

NOTE: if pydantic is not installed they will provide no actual functionality
(but they shouldn't crash either)
"""


class MockPydModel:
    """Mock pydantic model for use when pydantic is not installed."""

    def __init__(self, **kwargs):
        """Set attributes from kwargs."""
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockModule:
    """Mock pydantic module for use when pydantic is not installed."""

    def __getattr__(self, name):
        """Return a mock pydantic model."""
        return MockPydModel


try:
    import pydantic

    if pydantic.__version__.startswith("2"):
        from .project import ProjectModel
    else:
        msg = "Pydantic version is not 2.x.  Use mocked models."
        raise ImportError(msg)
except ImportError:
    # Mock the data models
    globals().update(
        {
            "projectcard_pyc": MockModule(),
        }
    )
