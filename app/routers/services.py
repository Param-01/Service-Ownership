import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.service import Service, ServiceStatus
from app.models.team import Team
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate
from app.schemas.summary import SummaryResponse, TeamSummaryItem

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceRead])
def list_services(team_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    q = db.query(Service).options(selectinload(Service.team))
    if team_id is not None:
        q = q.filter(Service.team_id == team_id)
    return q.all()


@router.get("/summary", response_model=SummaryResponse)
def get_summary(team_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    if team_id is not None:
        counts = (
            db.query(Service.status, func.count().label("n"))
            .filter(Service.team_id == team_id)
            .group_by(Service.status)
            .all()
        )
        count_map = {status: n for status, n in counts}
        total_active = count_map.get(ServiceStatus.ACTIVE, 0)
        total_deprecated = count_map.get(ServiceStatus.DEPRECATED, 0)
        total_services = total_active + total_deprecated

        team = db.query(Team).options(selectinload(Team.service)).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        teams_list = [TeamSummaryItem(team_id=team.id, team_name=team.name, service=team.service)]
        total_teams = 1
    else:
        counts = (
            db.query(Service.status, func.count().label("n"))
            .group_by(Service.status)
            .all()
        )
        count_map = {status: n for status, n in counts}
        total_active = count_map.get(ServiceStatus.ACTIVE, 0)
        total_deprecated = count_map.get(ServiceStatus.DEPRECATED, 0)
        total_services = total_active + total_deprecated

        all_teams = db.query(Team).options(selectinload(Team.service)).all()
        total_teams = len(all_teams)
        teams_list = [
            TeamSummaryItem(team_id=t.id, team_name=t.name, service=t.service)
            for t in all_teams
        ]

    return SummaryResponse(
        total_services=total_services,
        total_active=total_active,
        total_deprecated=total_deprecated,
        total_teams=total_teams,
        teams=teams_list,
    )


@router.post("", response_model=ServiceRead, status_code=201)
def create_service(body: ServiceCreate, db: Session = Depends(get_db)):
    team = db.query(Team).options(selectinload(Team.service)).filter(Team.id == body.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.service is not None:
        raise HTTPException(status_code=409, detail="Team already owns a service")

    service = Service(name=body.name, description=body.description, team_id=body.team_id)
    db.add(service)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Service name already exists")

    db.refresh(service)
    return db.query(Service).options(selectinload(Service.team)).filter(Service.id == service.id).one()


@router.patch("/{service_id}", response_model=ServiceRead)
def update_service(service_id: uuid.UUID, body: ServiceUpdate, db: Session = Depends(get_db)):
    service = db.query(Service).options(selectinload(Service.team)).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if "name" in body.model_fields_set:
        if body.name is None:
            raise HTTPException(status_code=422, detail="name cannot be set to null")
        service.name = body.name
    if "description" in body.model_fields_set:
        service.description = body.description
    if "team_id" in body.model_fields_set:
        new_team_id = body.team_id
        if new_team_id is not None:
            new_team = db.query(Team).options(selectinload(Team.service)).filter(Team.id == new_team_id).first()
            if not new_team:
                raise HTTPException(status_code=404, detail="Team not found")
            if new_team.service is not None and new_team.service.id != service_id:
                raise HTTPException(status_code=409, detail="Team already owns a service")
        service.team_id = new_team_id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Service name already exists")

    db.refresh(service)
    return db.query(Service).options(selectinload(Service.team)).filter(Service.id == service.id).one()


@router.post("/{service_id}/deprecate", response_model=ServiceRead)
def deprecate_service(service_id: uuid.UUID, db: Session = Depends(get_db)):
    service = db.query(Service).options(selectinload(Service.team)).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    if service.status == ServiceStatus.DEPRECATED:
        raise HTTPException(status_code=400, detail="Service is already deprecated")

    service.status = ServiceStatus.DEPRECATED
    service.deprecated_at = datetime.now(timezone.utc)
    service.team_id = None
    db.commit()
    db.refresh(service)
    return db.query(Service).options(selectinload(Service.team)).filter(Service.id == service.id).one()
