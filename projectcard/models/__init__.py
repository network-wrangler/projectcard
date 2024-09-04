"""Access to pydantic data models for the projectcard package generated from /schema jsonschema files.

NOTE: if pandera is not installed they will provide no actual functionality
(but they shouldn't crash either)
"""


class MockPydModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


try:
    import pydantic

    if pydantic.__version__.startswith("2"):
        from .generated.v2 import *
    else:
        from .records import *
except ImportError:
    # Mock the data models
    globals().update(
        {
            "generated": MockModule(),
        }
    )
