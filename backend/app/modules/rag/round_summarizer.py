from openai.types.responses import ResponseInputParam

from .client import client
from .json_schema import SummaryRound
from .prompts.summary_round import PROMPTS


async def summary_round(text: str) -> SummaryRound:
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
        model="gpt-5.4-mini",
        input=messages,
        store=False,
        text_format=SummaryRound,
    )

    if response.output_parsed is None:
        raise ValueError("No output parsed")

    result = response.output_parsed
    return result
