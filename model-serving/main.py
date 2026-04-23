import uvicorn
from fastapi import FastAPI
from routers.reranker import router as reranker_router

app = FastAPI()


app.include_router(reranker_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
