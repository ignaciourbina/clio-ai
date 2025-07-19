import os
from pathlib import Path
import base64

import pytest
from fastapi.testclient import TestClient


def create_client(tmp_path: Path) -> TestClient:
    os.environ["DB_DIR"] = str(tmp_path)
    os.environ["API_KEY"] = "testkey"

    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pm-api"))

    import projects_db
    import app as app_module

    projects_db.init_db()
    return TestClient(app_module.app, headers={"X-API-Key": "testkey"})


@pytest.fixture()
def client(tmp_path: Path):
    return create_client(tmp_path)


def test_root(client: TestClient):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Agile Project Management API is running"}


def test_project_crud(client: TestClient):
    payload = {
        "project_id": "P-001",
        "name": "Test Project",
        "status": "Planned",
    }
    # create
    resp = client.post("/projects/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["project_id"] == "P-001"
    project_id = data["id"]

    # list
    resp = client.get("/projects/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # get
    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Project"

    # update
    resp = client.put(f"/projects/{project_id}", json={"status": "Active"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "Active"

    # delete
    resp = client.delete(f"/projects/{project_id}")
    assert resp.status_code == 204

    # confirm gone
    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 404


def test_dataset_raw_and_purge(client: TestClient):
    # ensure dataset raw returns valid base64
    resp = client.get("/api/dataset/raw")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    # decode base64 to bytes
    base64.b64decode(data["data"])  # should not raise

    # purge DB
    resp = client.delete("/api/dataset")
    assert resp.status_code == 200
    assert "database reset" in resp.json()["detail"]

    resp = client.get("/projects/")
    assert resp.status_code == 200
    assert resp.json() == []

