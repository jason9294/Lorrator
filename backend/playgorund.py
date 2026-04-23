from pydantic import BaseModel, Field


def SensitiveField(*args, **kwargs):
    extra = kwargs.pop("json_schema_extra", {})
    extra["sensitive"] = True
    return Field(*args, json_schema_extra=extra, **kwargs)


class LoginRequest(BaseModel):
    username: str
    password: str = Field(..., json_schema_extra={"sensitive": True})


login = LoginRequest(username="test", password="123456")

print(login.model_json_schema())
