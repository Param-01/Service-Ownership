# Service Ownership API

A REST API for tracking which team owns which service. Built with FastAPI, SQLAlchemy, and MySQL.

## Features

- **Team management** — register teams, update details
- **Service management** — create services, assign to teams, update, and deprecate
- **One-to-one constraint** — each team can own at most one service
- **Soft deprecation** — deprecated services are retained with a timestamp and unassigned from their team
- **Summary stats** — aggregate counts of active/deprecated services, optionally scoped to a team
- **Health check** — lightweight endpoint with DB probe for load balancers

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [MySQL](https://www.mysql.com/) via `pymysql`
- [Pydantic v2](https://docs.pydantic.dev/)
- [pytest](https://pytest.org/)

## Project Structure

```
app/
  main.py             # FastAPI app entry point
  database.py         # Engine, session, get_db dependency
  models/
    base.py           # Base, UUIDMixin, TimestampMixin
    team.py           # Team model
    service.py        # Service model + ServiceStatus enum
  routers/
    health.py         # GET /health
    teams.py          # POST /teams, PATCH /teams/{id}
    services.py       # Full CRUD + deprecate + summary
  schemas/
    team.py           # TeamCreate, TeamUpdate, TeamRead
    service.py        # ServiceCreate, ServiceUpdate, ServiceRead
    summary.py        # SummaryResponse, TeamSummaryItem
tests/
  unit/
    test_schemas.py   # Pydantic validation tests
  integration/
    test_health.py
    test_teams.py
    test_services.py
```

## Setup

### Prerequisites
- Python 3.11+
- MySQL 8.0+

### Install dependencies

```bash
pip install fastapi pymysql sqlalchemy uvicorn pytest httpx
```

### Environment

```bash
export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/service_ownership"
```

### Run

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check with DB probe |
| POST | `/teams` | Create a team |
| PATCH | `/teams/{team_id}` | Update a team |
| GET | `/services` | List services (optional `?team_id=`) |
| GET | `/services/summary` | Aggregate stats (optional `?team_id=`) |
| POST | `/services` | Create a service |
| PATCH | `/services/{service_id}` | Update a service |
| POST | `/services/{service_id}/deprecate` | Deprecate a service |

## Running Tests

Integration tests run against a real MySQL database (`service_ownership_test`). Create it first:

```bash
mysql -u root -p -e "CREATE DATABASE service_ownership_test;"
```

Then run:

```bash
python3 -m pytest tests/ -v
```
