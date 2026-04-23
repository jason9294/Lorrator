from openai import AsyncOpenAI

from app.core import get_settings

settings = get_settings()

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
