"""Integration tests for /teams endpoints."""
import uuid


# ---------------------------------------------------------------------------
# POST /teams
# ---------------------------------------------------------------------------

class TestCreateTeam:
    def test_happy_path(self, client):
        res = client.post("/teams", json={"name": "Backend"})
        assert res.status_code == 201
        body = res.json()
        assert body["name"] == "Backend"
        assert body["description"] is None
        assert body["service"] is None
        assert "id" in body
        assert "created_at" in body

    def test_with_description(self, client):
        res = client.post("/teams", json={"name": "Frontend", "description": "UI team"})
        assert res.status_code == 201
        assert res.json()["description"] == "UI team"

    def test_duplicate_name_returns_409(self, client):
        client.post("/teams", json={"name": "Platform"})
        res = client.post("/teams", json={"name": "Platform"})
        assert res.status_code == 409

    def test_missing_name_returns_422(self, client):
        res = client.post("/teams", json={"description": "No name"})
        assert res.status_code == 422

    def test_empty_name_returns_422(self, client):
        res = client.post("/teams", json={"name": ""})
        assert res.status_code == 422

    def test_whitespace_name_returns_422(self, client):
        res = client.post("/teams", json={"name": "   "})
        assert res.status_code == 422


# ---------------------------------------------------------------------------
# PATCH /teams/{team_id}
# ---------------------------------------------------------------------------

class TestUpdateTeam:
    def _create(self, client, name="Alpha", description=None):
        payload = {"name": name}
        if description is not None:
            payload["description"] = description
        return client.post("/teams", json=payload).json()

    def test_update_name(self, client):
        team = self._create(client, "OldName")
        res = client.patch(f"/teams/{team['id']}", json={"name": "NewName"})
        assert res.status_code == 200
        assert res.json()["name"] == "NewName"

    def test_update_description(self, client):
        team = self._create(client, "TeamA")
        res = client.patch(f"/teams/{team['id']}", json={"description": "New desc"})
        assert res.status_code == 200
        assert res.json()["description"] == "New desc"

    def test_clear_description_with_null(self, client):
        team = self._create(client, "TeamB", description="Some desc")
        res = client.patch(f"/teams/{team['id']}", json={"description": None})
        assert res.status_code == 200
        assert res.json()["description"] is None

    def test_empty_body_is_no_op(self, client):
        team = self._create(client, "TeamC")
        res = client.patch(f"/teams/{team['id']}", json={})
        assert res.status_code == 200
        assert res.json()["name"] == "TeamC"

    def test_null_name_returns_422(self, client):
        team = self._create(client, "TeamD")
        res = client.patch(f"/teams/{team['id']}", json={"name": None})
        assert res.status_code == 422

    def test_empty_name_returns_422(self, client):
        team = self._create(client, "TeamE")
        res = client.patch(f"/teams/{team['id']}", json={"name": ""})
        assert res.status_code == 422

    def test_not_found_returns_404(self, client):
        res = client.patch(f"/teams/{uuid.uuid4()}", json={"name": "Ghost"})
        assert res.status_code == 404

    def test_duplicate_name_returns_409(self, client):
        self._create(client, "Taken")
        team = self._create(client, "Free")
        res = client.patch(f"/teams/{team['id']}", json={"name": "Taken"})
        assert res.status_code == 409
