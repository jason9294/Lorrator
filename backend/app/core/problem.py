from typing import Any, Optional

from pydantic import BaseModel, Field

PROBLEM_CONTENT_TYPE = "application/problem+json"


class ProblemDetails(BaseModel):
    # RFC 9457 core members
    type: str = Field(default="about:blank")  # URI or "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None

    # Extensions: accept arbitrary extra members
    model_config = {"extra": "allow"}


class ProblemException(Exception):
    def __init__(
        self,
        status_code: int,
        type: str | None = None,
        title: str | None = None,
        detail: Optional[str] = None,
        instance: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(detail)
        self.problem = ProblemDetails(
            type=type or "about:blank",
            title=title or "Unknown Error",
            status=status_code,
            detail=detail,
            instance=instance,
            **kwargs,
        )
