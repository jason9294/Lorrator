from fastapi import FastAPI
from fastapi.routing import APIRoute
from scalar_fastapi import get_scalar_api_reference

from app.core.setting import get_settings

from ..middlewares import register_middlewares
from .lifespan import lifespan
from .register_routers import register_routers


def custom_generate_unique_id(route: APIRoute):
    """
    自定義生成唯一 ID 的函數
    將 endpoint 的第一個 tag + 名稱組成
    """
    return f"{route.tags[0]}-{route.name}"


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        lifespan=lifespan,
        version="0.1.0",
        generate_unique_id_function=custom_generate_unique_id,
    )

    register_middlewares(app)
    register_routers(app)

    @app.get("/scalar", tags=["scalar"], include_in_schema=False)
    async def scalar_html():
        return get_scalar_api_reference(
            # Your OpenAPI document
            openapi_url=app.openapi_url,
            title=f"{settings.APP_NAME} - Scalar",
            # Avoid CORS issues (optional)
            scalar_proxy_url="https://proxy.scalar.com",
        )

    return app
