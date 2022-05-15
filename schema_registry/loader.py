import json
from pathlib import Path
from typing import Any

import aiofiles


class Loader:
    def __init__(self, schemas_root_path: Path):
        self._schemas_root_path = schemas_root_path
        self._schemas = {}

    async def schema(self, name: str, version: int) -> dict[str, Any]:
        schema_path = self._get_schema_path(name, version)
        try:
            return self._schemas[schema_path]
        except KeyError:
            schema = await self._load_schema(schema_path)
            self._schemas[schema_path] = schema
            return schema

    def _get_schema_path(self, name: str, version: int) -> Path:
        return self._schemas_root_path.joinpath(*name.split("."), f"{version}.json")

    async def _load_schema(self, schema_path: Path):
        async with aiofiles.open(schema_path) as schema_file:
            return json.loads(await schema_file.read())
