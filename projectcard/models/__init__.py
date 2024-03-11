"""
Access to pydantic and pandera data models for projectcard.

NOTE: if pandera is not installed they will provide no actual functionality
(but they shouldn't crash either)
"""


class MockPydModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


try:
    import pydantic

    if pydantic.__version__.startswith('1'):
        raise ImportError
    else:
        from .records import *
except ImportError:
    # Mock the data models
    globals().update(
        {
            '*': MockPydModel(),
        }
    )
