from openai.types.responses import ResponseInputParam

from .client import client
from .json_schema import ExtractedEntities
from .prompts.entity_extraction import PROMPTS


async def entity_extract(text: str) -> ExtractedEntities:
    print(f"entity_extract: {text[:100]} + ...")
    messages: ResponseInputParam = [
        {
            "role": "system",
            "content": PROMPTS["trpg_kg_extraction_system_prompt"],
        },
        {
            "role": "user",
            "content": PROMPTS["trpg_kg_extraction_user_prompt"] + text,
        },
    ]
    response = await client.responses.parse(
        model="gpt-5.4-mini",
        input=messages,
        store=False,
        text_format=ExtractedEntities,
    )

    if response.output_parsed is None:
        raise ValueError("No output parsed")

    result = response.output_parsed

    # prepare the messages for the continue extraction
    messages.append(
        {
            "role": "assistant",
            "content": response.output_text,
        }
    )
    messages.append(
        {
            "role": "user",
            "content": PROMPTS["trpg_kg_continue_extraction_user_prompt"],
        }
    )

    response = await client.responses.parse(
        model="gpt-5.4-mini",
        input=messages,
        store=False,
        text_format=ExtractedEntities,
    )

    if response.output_parsed is None:
        raise ValueError("No output parsed")

    continue_result = response.output_parsed

    result.entities.extend(continue_result.entities)
    result.relationships.extend(continue_result.relationships)

    return result


if __name__ == "__main__":
    import asyncio

    async def main():
        result = await entity_extract("""運》判定，決定身上的所持物品的去留。\n\n車廂門扉上有貼著一張紙條筆記\n「只管前進吧 已經沒有退路了」\n若對紙條筆記使用《觀察》\n紙條背後寫著「第三個箱子裡有藏著鑰匙」\n在這裡箱子指的是車廂，是3號車廂有藏著某個東西的鑰匙的提示\n\n另外，門扉旁邊有寫著電車的示意地圖，用《靈感》判定成功後可以得知7號車廂以後的地方是被人蓄意塗掉的\n(失敗的話大概就是只知道後面看不清楚之類的吧)\n\n<7號車廂>\n如果要前往7號車廂，要做《靈感》判定\n成功:感覺到一股血腥臭味，並覺得不太應該再繼續向前進 SAN0/1\n失敗:感覺到一股血腥臭味，但還是繼續往前進，打開門看見了悲慘被撕裂的人體似的東西散落一地 SAN1d3/1d4\n\n若是先前《靈感》成功的人看到的話SAN0/1\n使用《醫學》調查屍體可以發現它距離死亡的時間並沒有很久\n使用《觀察》\n\n成功:7號車輛深處有著巨大類似嘴巴的東西正在啃蝕車廂，可以理解那是某個比電車還要巨大的存在 SAN1/2\n失敗:原本應該要存在7號車廂往8號車廂的門不見了，只存在著一片漆黑。\n\n<5號車廂>\n\n《觀察》成功的話可以找到報紙\n內容:昨晚OO線電車發生了大規模的恐怖事件，雖然還未被確認為恐怖分子所為。\n不過倖存乘客的精神變得異常，全部都送往了精神病院。\n疑點重重，搜查難以進行。\n\n對報紙使用《使用圖書館》或是《觀察》\n成功:可以得知報紙上面的事件是和現在同一年同一天發生的事情，隨後意識到這是來自明天的報紙。SAN0/1\n\n在這裡是用《靈感》判定\n成功6號車廂已經有快要一半的部分要消失了SAN0/1\n失敗:並沒有特別什麼感覺\n※若有行動限制的規則:在超過限制的行動回合時，伴隨著5號車廂那一邊的門扉發出了叭哩叭哩的聲響，腳下的立足點正慢慢地消失，雖然可以用跑的逃跑，
    """)
        print(result.model_dump_json(indent=2))

    asyncio.run(main())
