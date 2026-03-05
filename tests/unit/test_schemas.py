"""Unit tests for Pydantic schema validation."""
import uuid

import pytest
from pydantic import ValidationError

from app.schemas.service import ServiceCreate, ServiceUpdate
from app.schemas.team import TeamCreate, TeamUpdate


class TestTeamCreate:
    def test_valid(self):
        t = TeamCreate(name="Backend")
        assert t.name == "Backend"
        assert t.description is None

    def test_with_description(self):
        t = TeamCreate(name="Backend", description="Handles backend services")
        assert t.description == "Handles backend services"

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            TeamCreate()

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            TeamCreate(name="")

    def test_whitespace_name_raises(self):
        with pytest.raises(ValidationError):
            TeamCreate(name="   ")


class TestTeamUpdate:
    def test_empty_body_is_valid(self):
        t = TeamUpdate()
        assert t.model_fields_set == set()

    def test_name_only(self):
        t = TeamUpdate(name="New Name")
        assert "name" in t.model_fields_set
        assert "description" not in t.model_fields_set

    def test_description_can_be_null(self):
        t = TeamUpdate(description=None)
        assert "description" in t.model_fields_set
        assert t.description is None

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            TeamUpdate(name="")

    def test_whitespace_name_raises(self):
        with pytest.raises(ValidationError):
            TeamUpdate(name="  ")


class TestServiceCreate:
    def test_valid(self):
        team_id = uuid.uuid4()
        s = ServiceCreate(name="Auth Service", team_id=team_id)
        assert s.name == "Auth Service"
        assert s.team_id == team_id

    def test_missing_team_id_raises(self):
        with pytest.raises(ValidationError):
            ServiceCreate(name="Auth Service")

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            ServiceCreate(team_id=uuid.uuid4())

    def test_invalid_team_id_raises(self):
        with pytest.raises(ValidationError):
            ServiceCreate(name="Auth Service", team_id="not-a-uuid")


class TestServiceUpdate:
    def test_empty_body_is_valid(self):
        s = ServiceUpdate()
        assert s.model_fields_set == set()

    def test_team_id_can_be_null(self):
        s = ServiceUpdate(team_id=None)
        assert "team_id" in s.model_fields_set
        assert s.team_id is None

    def test_partial_update_tracks_fields(self):
        s = ServiceUpdate(name="New Name")
        assert "name" in s.model_fields_set
        assert "description" not in s.model_fields_set
        assert "team_id" not in s.model_fields_set
