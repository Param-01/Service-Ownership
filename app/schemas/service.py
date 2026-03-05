import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.service import ServiceStatus


class ServiceReadBrief(BaseModel):
    id: uuid.UUID
    name: str
    status: ServiceStatus

    model_config = {"from_attributes": True}


class TeamReadBrief(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class ServiceCreate(BaseModel):
    name: str
    team_id: uuid.UUID
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be empty")
        return v


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    team_id: uuid.UUID | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name cannot be empty")
        return v


class ServiceDeprecate(BaseModel):
    reason: str | None = None


class ServiceRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    status: ServiceStatus
    team_id: uuid.UUID | None
    deprecated_at: datetime | None
    created_at: datetime
    updated_at: datetime
    team: TeamReadBrief | None = None

    model_config = {"from_attributes": True}
