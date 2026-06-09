import json

from openai.types.responses import ResponseInputParam

from .client import client
from .json_schema import EntityGroup, EntityGroupChunk, EntityGroupEntity
from .prompts.entity_group import PROMPTS


async def entity_group(
    chunks: list[EntityGroupChunk],
    entities: list[EntityGroupEntity],
) -> EntityGroup:
    user_content = "```chunks\n"
    user_content += json.dumps(
        [c.model_dump() for c in chunks], ensure_ascii=False, indent=2
    )
    user_content += "\n```\n\n"
    user_content += "```entities\n"
    user_content += json.dumps(
        [e.model_dump() for e in entities], ensure_ascii=False, indent=2
    )
    user_content += "\n```\n"
    user_content += "Now begin grouping and replying in the original language."

    messages: ResponseInputParam = [
        {
            "role": "system",
            "content": PROMPTS["entity_group_system_prompt"],
        },
        {
            "role": "user",
            "content": user_content,
        },
    ]
    response = await client.responses.parse(
        model="gpt-5.4-mini",
        input=messages,
        store=False,
        text_format=EntityGroup,
    )

    if response.output_parsed is None:
        raise ValueError("No output parsed")

    return response.output_parsed
