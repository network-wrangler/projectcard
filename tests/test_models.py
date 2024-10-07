import pytest
from pydantic import ValidationError, validate_call

from projectcard import CardLogger


@pytest.fixture(scope="session")
def pyd_data_models():
    from pydantic import BaseModel

    from projectcard import models

    data_models = []
    CardLogger.info(f"MODELS:\n{dir(models)}")
    for attribute_name in dir(models):
        attribute = getattr(models, attribute_name)
        if isinstance(attribute, type) and issubclass(attribute, BaseModel):
            data_models.append(attribute)
    return data_models


def test_models_to_examples(pyd_data_models):
    models_with_ex = [m for m in pyd_data_models if hasattr(m, "example")]
    CardLogger.info(f"Found {len(models_with_ex)} PYD models w/examples of {len(pyd_data_models)}")
    for model in models_with_ex:
        CardLogger.info(f"Evaluating examples for: {model}")
        # For each example, validate the example against the model
        for example in model.example:
            model(**example)


def test_using_validate_call_models_with_pyd():
    valid_data = {"links": {"model_link_id": [1234], "lanes": [2, 3]}}

    invalid_data = {"links": {"model_link_id": 1234}}

    from projectcard.models.selections import SelectFacility

    @validate_call
    def select_segment_in(data: SelectFacility):
        # Add your function code here
        pass

    # Test with valid data
    select_segment_in(valid_data)

    # Test with invalid data
    with pytest.raises(ValidationError):
        select_segment_in(invalid_data)


def test_instantiating_data_models_with_pyd():
    # Create valid and invalid data instances
    from projectcard.models.selections import SelectTransitTrips

    valid_data = {
        "trip_properties": {"trip_id": ["1234"]},
        "route_properties": {"agency_id": [4321]},  # should coerce this to a string
        "timespans": [["12:45", "12:30"]],
    }

    invalid_data = {"timespan": ["123", "123"]}

    SelectTransitTrips(**valid_data)

    # Test with invalid data
    with pytest.raises(ValidationError):
        SelectTransitTrips(**invalid_data)
