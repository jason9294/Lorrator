from pydantic import BaseModel, Field, model_validator


class CreateScenarioRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    system: str = Field(min_length=1, max_length=50, description="COC, DND, etc.")

    min_players: int | None = Field(default=None, ge=1)
    max_players: int | None = Field(default=None, ge=1)

    min_hours: float | None = Field(default=None, ge=1)
    max_hours: float | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _validate_ranges(self):
        if (
            self.min_players is not None
            and self.max_players is not None
            and self.min_players > self.max_players
        ):
            raise ValueError("min_players must be <= max_players")
        if (
            self.min_hours is not None
            and self.max_hours is not None
            and self.min_hours > self.max_hours
        ):
            raise ValueError("min_hours must be <= max_hours")
        return self


class UpdateScenarioRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    system: str | None = Field(default=None, min_length=1, max_length=50)

    min_players: int | None = Field(default=None, ge=1)
    max_players: int | None = Field(default=None, ge=1)

    min_hours: float | None = Field(default=None, ge=1)
    max_hours: float | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _validate_ranges(self):
        if (
            self.min_players is not None
            and self.max_players is not None
            and self.min_players > self.max_players
        ):
            raise ValueError("min_players must be <= max_players")
        if (
            self.min_hours is not None
            and self.max_hours is not None
            and self.min_hours > self.max_hours
        ):
            raise ValueError("min_hours must be <= max_hours")
        return self


class CreateRoomRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
