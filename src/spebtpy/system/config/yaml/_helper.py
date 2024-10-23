import sys
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7
import json
import spebtpy.system.config.schema

if sys.version_info < (3, 10):
    from importlib_resources import files as _files
else:
    from importlib.resources import files as _files


def get_schema_registry(version: str = "v1"):
    # Load the schema
    _schema_dir = f"spebtpy.system.config.schema.{version}"
    _basenames = ["main", "detector", "relation", "FOV", "transformation_data"]

    schema_registry = Registry()
    for basename in _basenames:
        # loaded = Resource(
        #     contents=json.load(open(f"{str(_schema_dir)}/{_basename}.json", "r")),
        #     specification=DRAFT7,
        # )
        loaded = Resource(
            contents=json.loads(
                _files(_schema_dir).joinpath(f"{basename}.json").read_text()
            ),
            specification=DRAFT7,
        )
        schema_registry = loaded @ schema_registry
    return schema_registry
