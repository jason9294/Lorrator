from functools import lru_cache

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = Field(default="FastAPI")
    SECRET_KEY: str = Field(default="change_me")

    DATABASE_USERNAME: str = Field(default="postgres")
    DATABASE_PASSWORD: str = Field(default="password")
    DATABASE_HOST: str = Field(default="localhost")
    DATABASE_PORT: int = Field(default=5432)
    DATABASE_NAME: str = Field(default="fastapi_db")

    #  Discord OAuth2 settings
    DISCORD_CLIENT_ID: str = Field(default="")
    DISCORD_CLIENT_SECRET: str = Field(default="")
    DISCORD_REDIRECT_URI: str = Field(default="")

    RERANKER_URL: str = Field(default="")

    # 劇本文件上傳根目錄（相對於進程工作目錄）
    UPLOAD_DIR: str = Field(default="uploads")

    OPENAI_API_KEY: str = Field(default="")
    EMBEDDING_DIM: int = Field(default=1536)

    NEO4J_URI: str = Field(default="bolt://localhost:7687")
    NEO4J_USER: str = Field(default="neo4j")
    NEO4J_PASSWORD: str = Field(default="password")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.DATABASE_USERNAME,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_HOST,
                port=self.DATABASE_PORT,
                path=self.DATABASE_NAME,
            )
        )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()  # type: ignore
    if settings.SECRET_KEY == "change_me":
        ...  # TODO warning
    return settings
