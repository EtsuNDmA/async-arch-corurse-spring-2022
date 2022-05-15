from pathlib import Path

from jsonschema import validate

from schema_registry.loader import Loader


class Validator:
    def __init__(self, schemas_root_path: Path):
        self._loader = Loader(schemas_root_path)

    async def validate(self, data, name, version=1):
        schema = await self._loader.schema(name, version)
        return validate(instance=data, schema=schema)
