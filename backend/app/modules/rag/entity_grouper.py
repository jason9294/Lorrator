import json
from typing import Any

from openai.types.responses import ResponseInputParam

from app.modules.document_pipeline.llm_recorder import LlmCallRecorder

from .client import client
from .json_schema import EntityGroup, EntityGroupChunk, EntityGroupEntity
from .prompts.entity_group import PROMPTS

ENTITY_GROUP_MODEL = "gpt-5.4-mini"


def _serialize_messages(messages: ResponseInputParam) -> list[dict[str, Any]]:
    return [dict(message) for message in messages]


async def entity_group(
    chunks: list[EntityGroupChunk],
    entities: list[EntityGroupEntity],
    *,
    recorder: LlmCallRecorder | None = None,
    step_id: str | None = None,
    iteration: int | None = None,
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
        model=ENTITY_GROUP_MODEL,
        input=messages,
        store=False,
        text_format=EntityGroup,
    )

    if response.output_parsed is None:
        raise ValueError("No output parsed")

    result = response.output_parsed

    if recorder is not None and step_id is not None and iteration is not None:
        await recorder.record(
            step_id=step_id,
            call_key=f"iteration_{iteration}",
            label=f"第 {iteration} 輪分群",
            model=ENTITY_GROUP_MODEL,
            request=_serialize_messages(messages),
            response=result.model_dump(mode="json"),
        )

    return result
