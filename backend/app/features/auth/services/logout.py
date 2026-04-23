from fastapi import Response

from app.core.security import TOKEN_COOKIE_NAME


class LogoutService:
    async def execute(self, response: Response) -> dict[str, str]:
        response.delete_cookie(key=TOKEN_COOKIE_NAME, path="/")
        return {"message": "User logged out successfully"}
