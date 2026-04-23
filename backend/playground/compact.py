import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Full window collected from prior turns
long_input_items_array = [
    {
        "type": "message",
        "role": "system",
        "content": "你是一個負責協助使用者進行技術問題分析與解決的 AI 助手，需提供精確且具邏輯性的回應。",
    },
    {
        "type": "message",
        "role": "user",
        "content": "我正在設計一個 API，想知道如何在高併發情境下維持效能？",
    },
    {
        "type": "message",
        "role": "assistant",
        "content": "在高併發場景中，API 設計需關注以下幾點：\n1. 使用非同步處理（例如 async/await）避免阻塞。\n2. 引入快取機制（如 Redis）降低資料庫負載。\n3. 實作連線池以有效管理資源。\n4. 使用負載平衡（Load Balancer）分散流量。\n5. 設計無狀態服務（Stateless）以利水平擴展。",
    },
    {
        "type": "message",
        "role": "user",
        "content": "那如果我要用 FastAPI，有什麼具體建議？",
    },
    {
        "type": "message",
        "role": "assistant",
        "content": "在 FastAPI 中，可以採取以下策略優化高併發效能：\n1. 使用 uvicorn 搭配 gunicorn 作為 ASGI server。\n2. 啟用 async endpoint 並避免同步 I/O。\n3. 整合 Redis 作為快取層。\n4. 使用資料庫連線池（例如 asyncpg）。\n5. 搭配 Nginx 作反向代理與負載平衡。",
    },
]

# 1) Compact the current window
compacted = client.responses.compact(
    model="gpt-5.4",
    input=long_input_items_array,
)

import json

with open("playground/compacted.json", "w", encoding="utf-8") as f:
    json.dump(compacted.model_dump(), f, indent=4, ensure_ascii=False)


# 2) Start the next turn by appending a new user message
# next_input = [
#     *compacted.output,  # Use compact output as-is
#     {
#         "type": "message",
#         "role": "user",
#         "content": user_input_message(),
#     },
# ]

# next_response = client.responses.create(
#     model="gpt-5.4",
#     input=next_input,
#     store=False,  # Keep the flow ZDR-friendly
# )
