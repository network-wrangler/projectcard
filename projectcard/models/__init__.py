"""Access to pydantic data models for the projectcard package generated from /schema jsonschema files.

Checks if pydantic v1 vs v2 is installed and imports corresponding data models.
If pydantic is not installed, its functionality will be "mocked" so that the project card package
can be used without pydantic.

NOTE: if pydantic is not installed they will provide no actual functionality
(but they shouldn't crash either)
"""


class MockPydModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockModule:
    def __getattr__(self, name):
        return MockPydModel


try:
    import pydantic

    if pydantic.__version__.startswith("2"):
        from .generated.v2 import *
    else:
        from .generated.v1 import *
except ImportError:
    # Mock the data models
    globals().update(
        {
            "generated": MockModule(),
        }
    )
