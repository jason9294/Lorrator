from typing import Any

from openai.types.responses import ResponseInputParam

from app.modules.document_pipeline.llm_recorder import LlmCallRecorder

from .client import client
from .json_schema import SummaryRound
from .prompts.summary_round import PROMPTS

SUMMARY_ROUND_MODEL = "gpt-5.4-mini"
ROUND_SUMMARIZER_STEP_ID = "round_summarizer"


def _serialize_messages(messages: ResponseInputParam) -> list[dict[str, Any]]:
    return [dict(message) for message in messages]


async def summary_round(
    text: str,
    *,
    recorder: LlmCallRecorder | None = None,
) -> SummaryRound:
    messages: ResponseInputParam = [
        {
            "role": "system",
            "content": PROMPTS["summary_round_system_prompt"],
        },
        {
            "role": "user",
            "content": text,
        },
    ]
    response = await client.responses.parse(
        model=SUMMARY_ROUND_MODEL,
        input=messages,
        store=False,
        text_format=SummaryRound,
    )

    if response.output_parsed is None:
        raise ValueError("No output parsed")

    result = response.output_parsed

    if recorder is not None:
        await recorder.record(
            step_id=ROUND_SUMMARIZER_STEP_ID,
            call_key="summary_round",
            label="回合摘要",
            model=SUMMARY_ROUND_MODEL,
            request=_serialize_messages(messages),
            response=result.model_dump(mode="json"),
        )

    return result
