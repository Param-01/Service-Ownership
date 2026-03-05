import uuid

from pydantic import BaseModel

from .service import ServiceReadBrief


class TeamSummaryItem(BaseModel):
    team_id: uuid.UUID
    team_name: str
    service: ServiceReadBrief | None

    model_config = {"from_attributes": True}


class SummaryResponse(BaseModel):
    total_services: int
    total_active: int
    total_deprecated: int
    total_teams: int
    teams: list[TeamSummaryItem]
