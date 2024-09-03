
from projectcard.validate import update_dict_with_schema_defaults


def test_update_dict_with_schema_defaults():
    # Test case 1: Missing required property with default value
    data = {}
    schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "default": "John Doe",
            },
            "age": {
                "type": "integer",
                "default": 30,
            },
        },
        "required": ["name"],
    }
    expected_result = {
        "name": "John Doe",
    }
    assert update_dict_with_schema_defaults(data, schema) == expected_result

    # Test case 2: Required property already present
    data = {
        "name": "Jane Smith",
    }
    expected_result = {
        "name": "Jane Smith",
    }
    assert update_dict_with_schema_defaults(data, schema) == expected_result

    # Test case 3: Nested properties with default values
    data = {
        "person": {
            "name": "Alice",
        },
    }
    schema = {
        "type": "object",
        "properties": {
            "person": {
                "type": "object",
                "required": ["name", "age"],
                "properties": {
                    "name": {
                        "type": "string",
                        "default": "John Doe",
                    },
                    "age": {
                        "type": "integer",
                        "default": 30,
                    },
                },
            },
        },
    }
    expected_result = {
        "person": {
            "name": "Alice",
            "age": 30,
        },
    }
    assert update_dict_with_schema_defaults(data, schema) == expected_result

    # Test case 4: List items with default values
    data = {
        "people": [
            {
                "name": "Bob",
            },
            {
                "name": "Charlie",
                "age": 25,
            },
            {},
        ],
    }
    schema = {
        "type": "object",
        "properties": {
            "people": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "age"],
                    "properties": {
                        "name": {
                            "type": "string",
                            "default": "John Doe",
                        },
                        "age": {
                            "type": "integer",
                            "default": 30,
                        },
                    },
                },
            },
        },
    }
    expected_result = {
        "people": [
            {
                "name": "Bob",
                "age": 30,
            },
            {
                "name": "Charlie",
                "age": 25,
            },
            {
                "name": "John Doe",
                "age": 30,
            },
        ],
    }
    assert update_dict_with_schema_defaults(data, schema) == expected_result
