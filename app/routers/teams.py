import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamRead, TeamUpdate

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamRead, status_code=201)
def create_team(body: TeamCreate, db: Session = Depends(get_db)):
    team = Team(name=body.name, description=body.description)
    db.add(team)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Team name already exists")
    return db.query(Team).options(selectinload(Team.service)).filter(Team.id == team.id).one()


@router.patch("/{team_id}", response_model=TeamRead)
def update_team(team_id: uuid.UUID, body: TeamUpdate, db: Session = Depends(get_db)):
    team = db.query(Team).options(selectinload(Team.service)).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if "name" in body.model_fields_set:
        if body.name is None:
            raise HTTPException(status_code=422, detail="name cannot be set to null")
        team.name = body.name
    if "description" in body.model_fields_set:
        team.description = body.description

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Team name already exists")

    db.refresh(team)
    return db.query(Team).options(selectinload(Team.service)).filter(Team.id == team.id).one()
