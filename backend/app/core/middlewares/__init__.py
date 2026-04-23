from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # 本機端（指定端口，例如前端應用程式）
            "http://127.0.0.1:5173",
            "http://10.144.1.110:5173",
            "http://10.144.1.101:5173",
        ],
        allow_credentials=True,  # 若需要允許 cookies，設為 True
        allow_methods=["*"],  # 設定允許的方法，["*"] 代表所有方法
        allow_headers=["*"],  # 設定允許的 headers，["*"] 代表所有 headers
        expose_headers=["Content-Type", "Set-Cookie"],
    )
