"""Integration tests for /services endpoints."""
import uuid


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def create_team(client, name="Alpha"):
    return client.post("/teams", json={"name": name}).json()


def create_service(client, name, team_id, description=None):
    payload = {"name": name, "team_id": str(team_id)}
    if description:
        payload["description"] = description
    return client.post("/services", json=payload)


# ---------------------------------------------------------------------------
# POST /services
# ---------------------------------------------------------------------------

class TestCreateService:
    def test_happy_path(self, client):
        team = create_team(client, "Backend")
        res = create_service(client, "Auth Service", team["id"])
        assert res.status_code == 201
        body = res.json()
        assert body["name"] == "Auth Service"
        assert body["status"] == "active"
        assert body["team_id"] == team["id"]
        assert body["team"]["name"] == "Backend"
        assert body["deprecated_at"] is None

    def test_with_description(self, client):
        team = create_team(client, "Data")
        res = create_service(client, "Pipeline", team["id"], description="ETL pipeline")
        assert res.status_code == 201
        assert res.json()["description"] == "ETL pipeline"

    def test_team_not_found_returns_404(self, client):
        res = create_service(client, "Orphan", uuid.uuid4())
        assert res.status_code == 404

    def test_team_already_has_service_returns_409(self, client):
        team = create_team(client, "Infra")
        create_service(client, "First", team["id"])
        res = create_service(client, "Second", team["id"])
        assert res.status_code == 409

    def test_duplicate_service_name_returns_409(self, client):
        team1 = create_team(client, "Team1")
        team2 = create_team(client, "Team2")
        create_service(client, "SharedName", team1["id"])
        res = create_service(client, "SharedName", team2["id"])
        assert res.status_code == 409

    def test_missing_team_id_returns_422(self, client):
        res = client.post("/services", json={"name": "NoTeam"})
        assert res.status_code == 422

    def test_empty_name_returns_422(self, client):
        team = create_team(client, "TeamX")
        res = create_service(client, "", team["id"])
        assert res.status_code == 422


# ---------------------------------------------------------------------------
# GET /services
# ---------------------------------------------------------------------------

class TestListServices:
    def test_empty_list(self, client):
        res = client.get("/services")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_all_services(self, client):
        t1 = create_team(client, "T1")
        t2 = create_team(client, "T2")
        create_service(client, "Svc1", t1["id"])
        create_service(client, "Svc2", t2["id"])
        res = client.get("/services")
        assert res.status_code == 200
        assert len(res.json()) == 2

    def test_filter_by_team_id(self, client):
        t1 = create_team(client, "FilterTeam1")
        t2 = create_team(client, "FilterTeam2")
        create_service(client, "SvcA", t1["id"])
        create_service(client, "SvcB", t2["id"])
        res = client.get(f"/services?team_id={t1['id']}")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["name"] == "SvcA"

    def test_filter_by_nonexistent_team_returns_empty(self, client):
        res = client.get(f"/services?team_id={uuid.uuid4()}")
        assert res.status_code == 200
        assert res.json() == []


# ---------------------------------------------------------------------------
# GET /services/summary
# ---------------------------------------------------------------------------

class TestSummary:
    def test_empty_summary(self, client):
        res = client.get("/services/summary")
        assert res.status_code == 200
        body = res.json()
        assert body["total_services"] == 0
        assert body["total_active"] == 0
        assert body["total_deprecated"] == 0
        assert body["total_teams"] == 0
        assert body["teams"] == []

    def test_summary_counts(self, client):
        t1 = create_team(client, "SumTeam1")
        t2 = create_team(client, "SumTeam2")
        svc = create_service(client, "ActiveSvc", t1["id"]).json()
        create_service(client, "DeprecatedSvc", t2["id"])
        client.post(f"/services/{svc['id']}/deprecate")

        res = client.get("/services/summary")
        body = res.json()
        assert body["total_services"] == 2
        assert body["total_active"] == 1
        assert body["total_deprecated"] == 1
        assert body["total_teams"] == 2

    def test_summary_filtered_by_team(self, client):
        t1 = create_team(client, "FilteredTeam")
        t2 = create_team(client, "OtherTeam")
        create_service(client, "S1", t1["id"])
        create_service(client, "S2", t2["id"])

        res = client.get(f"/services/summary?team_id={t1['id']}")
        body = res.json()
        assert body["total_services"] == 1
        assert body["total_teams"] == 1
        assert body["teams"][0]["team_name"] == "FilteredTeam"

    def test_summary_filtered_team_not_found(self, client):
        res = client.get(f"/services/summary?team_id={uuid.uuid4()}")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /services/{service_id}
# ---------------------------------------------------------------------------

class TestUpdateService:
    def _setup(self, client):
        team = create_team(client, "PatchTeam")
        svc = create_service(client, "PatchSvc", team["id"]).json()
        return team, svc

    def test_update_name(self, client):
        _, svc = self._setup(client)
        res = client.patch(f"/services/{svc['id']}", json={"name": "NewName"})
        assert res.status_code == 200
        assert res.json()["name"] == "NewName"

    def test_update_description(self, client):
        _, svc = self._setup(client)
        res = client.patch(f"/services/{svc['id']}", json={"description": "Updated desc"})
        assert res.status_code == 200
        assert res.json()["description"] == "Updated desc"

    def test_clear_description(self, client):
        team = create_team(client, "ClearDescTeam")
        svc = create_service(client, "ClearDescSvc", team["id"], description="old").json()
        res = client.patch(f"/services/{svc['id']}", json={"description": None})
        assert res.status_code == 200
        assert res.json()["description"] is None

    def test_unassign_team(self, client):
        _, svc = self._setup(client)
        res = client.patch(f"/services/{svc['id']}", json={"team_id": None})
        assert res.status_code == 200
        assert res.json()["team_id"] is None
        assert res.json()["team"] is None

    def test_reassign_team(self, client):
        _, svc = self._setup(client)
        new_team = create_team(client, "NewOwner")
        res = client.patch(f"/services/{svc['id']}", json={"team_id": new_team["id"]})
        assert res.status_code == 200
        assert res.json()["team"]["name"] == "NewOwner"

    def test_reassign_to_team_that_already_owns_service_returns_409(self, client):
        t1 = create_team(client, "Owner1")
        t2 = create_team(client, "Owner2")
        svc1 = create_service(client, "Svc1", t1["id"]).json()
        create_service(client, "Svc2", t2["id"])
        res = client.patch(f"/services/{svc1['id']}", json={"team_id": t2["id"]})
        assert res.status_code == 409

    def test_null_name_returns_422(self, client):
        _, svc = self._setup(client)
        res = client.patch(f"/services/{svc['id']}", json={"name": None})
        assert res.status_code == 422

    def test_empty_name_returns_422(self, client):
        _, svc = self._setup(client)
        res = client.patch(f"/services/{svc['id']}", json={"name": ""})
        assert res.status_code == 422

    def test_not_found_returns_404(self, client):
        res = client.patch(f"/services/{uuid.uuid4()}", json={"name": "Ghost"})
        assert res.status_code == 404

    def test_empty_body_is_no_op(self, client):
        _, svc = self._setup(client)
        res = client.patch(f"/services/{svc['id']}", json={})
        assert res.status_code == 200
        assert res.json()["name"] == "PatchSvc"


# ---------------------------------------------------------------------------
# POST /services/{service_id}/deprecate
# ---------------------------------------------------------------------------

class TestDeprecateService:
    def test_happy_path(self, client):
        team = create_team(client, "DepTeam")
        svc = create_service(client, "DepSvc", team["id"]).json()
        res = client.post(f"/services/{svc['id']}/deprecate")
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "deprecated"
        assert body["deprecated_at"] is not None
        assert body["team_id"] is None

    def test_already_deprecated_returns_400(self, client):
        team = create_team(client, "DepTeam2")
        svc = create_service(client, "DepSvc2", team["id"]).json()
        client.post(f"/services/{svc['id']}/deprecate")
        res = client.post(f"/services/{svc['id']}/deprecate")
        assert res.status_code == 400

    def test_not_found_returns_404(self, client):
        res = client.post(f"/services/{uuid.uuid4()}/deprecate")
        assert res.status_code == 404

    def test_team_no_longer_owns_deprecated_service(self, client):
        team = create_team(client, "FreeTeam")
        svc = create_service(client, "ToDeprecate", team["id"]).json()
        client.post(f"/services/{svc['id']}/deprecate")

        # team can now own a new service
        res = create_service(client, "NewService", team["id"])
        assert res.status_code == 201
