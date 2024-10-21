import sys
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7
import json

if sys.version_info < (3, 10):
    from importlib_resources import files as _files
else:
    from importlib.resources import files as _files


def get_schema_registry(version: str = "v1"):
    # Load the schema
    _schema_dir = _files(f"pyspebt.system.specification.schema.{version}")
    _basenames = ["main", "detector", "relation", "FOV", "transformation_data"]

    schema_registry = Registry()
    for _basename in _basenames:
        loaded = Resource(
            contents=json.load(open(f"{str(_schema_dir)}/{_basename}.json", "r")),
            specification=DRAFT7,
        )

        schema_registry = loaded @ schema_registry
    return schema_registry
