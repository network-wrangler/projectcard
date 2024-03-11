import pytest
from pydantic import ValidationError, validate_call

from projectcard import CardLogger


@pytest.fixture(scope="session")
def pyd_data_models(update_datamodels):
    from pydantic import BaseModel

    import projectcard.models as models

    data_models = []
    print(f"MODELS:\n{dir(models)}")
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

    from projectcard.models import SelectSegment

    @validate_call
    def select_segment_in(data: SelectSegment):
        # Add your function code here
        pass

    # Test with valid data
    select_segment_in(valid_data)

    # Test with invalid data
    try:
        select_segment_in(invalid_data)
    except ValidationError:
        pass
    else:
        assert False, "Invalid data should have raised a ValueError"


def test_instantiating_data_models_with_pyd():
    # Create valid and invalid data instances
    from projectcard.models import SelectTrips

    valid_data = {
        "trip_properties": {"trip_id": ["1234"]},
        "route_properties": {"agency_id": [4321]},
        "timespans": [["12:45", "12:30"]],
    }

    invalid_data = {"timespan": ["123", "123"]}

    SelectTrips(**valid_data)

    # Test with invalid data
    try:
        SelectTrips(**invalid_data)
    except ValidationError:
        pass
    else:
        assert False, "Invalid data should have raised a ValidationError"
