import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from .service import ServiceReadBrief


class TeamCreate(BaseModel):
    name: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be empty")
        return v


class TeamUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name cannot be empty")
        return v


class TeamReadBrief(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class TeamRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    service: ServiceReadBrief | None = None

    model_config = {"from_attributes": True}
