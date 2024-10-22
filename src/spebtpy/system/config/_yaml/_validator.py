from ._helper import get_schema_registry
from jsonschema import Draft7Validator


def validate(input: dict, name: str, version: str = "v1"):
    """
    Validates the given JSON data against the provided schema.
    """
    # Get the schema registry
    schema_registry = get_schema_registry(version=version)

    # Validate the JSON data
    validator = Draft7Validator(
        schema_registry[f"/{version}/{name}"].contents, registry=schema_registry
    )

    try:
        validator.validate(input)
    except Exception as e:
        raise e
