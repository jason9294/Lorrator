from copy import deepcopy

from pydantic import BaseModel, ConfigDict


class Entity(BaseModel):
    id: str
    name: str
    type: str
    description: str

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})


class Relationship(BaseModel):
    id: str
    source: str
    target: str
    type: str
    description: str

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})


class Data(BaseModel):
    entities: list[Entity]
    relationships: list[Relationship]

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})


def resolve_refs(schema: dict) -> dict:
    defs = schema.get("$defs", {})

    def _resolve(node):
        if isinstance(node, dict):
            if "$ref" in node:
                ref_path = node["$ref"]
                ref_key = ref_path.split("/")[-1]
                return _resolve(deepcopy(defs[ref_key]))

            return {k: _resolve(v) for k, v in node.items() if k != "$defs"}

        elif isinstance(node, list):
            return [_resolve(item) for item in node]

        return node

    resolved = _resolve(schema)
    resolved.pop("$defs", None)
    resolved.pop("title")  # type: ignore
    return resolved  # type: ignore


if __name__ == "__main__":
    import json

    schema = Data.model_json_schema()
    resolved_schema = resolve_refs(schema)

    result = {
        "name": "entities_and_relationships",
        "strict": True,
        "schema": resolved_schema,
    }

    with open("playground/data_inline.json", "w") as f:
        json.dump(result, f, indent=4)
