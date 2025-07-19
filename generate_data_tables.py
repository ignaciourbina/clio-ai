"""Run sample API requests and save project data as CSV."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from typing import List, Dict

OUTPUT_DIR = Path("data_tables_test")
DB_DIR = OUTPUT_DIR / "db"


def setup() -> None:
    """Prepare directories and environment variables for the test DB."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    DB_DIR.mkdir(exist_ok=True)
    for db_file in DB_DIR.glob("*.db"):
        db_file.unlink()
    os.environ["DB_DIR"] = str(DB_DIR)
    os.environ["API_KEY"] = "testkey"
    sys.path.insert(0, str(Path(__file__).resolve().parent / "pm-api"))


def save_table(path: Path, rows: List[Dict]) -> None:
    """Write a list of dictionaries to ``path`` as CSV."""
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    setup()

    from fastapi.testclient import TestClient  # noqa: E402
    import app as app_module  # noqa: E402
    import projects_db  # noqa: E402

    projects_db.init_db()
    client = TestClient(app_module.app, headers={"X-API-Key": "testkey"})

    project_payloads = [
        {
            "project_id": "P-101",
            "name": "AI assistant",
            "status": "Planned",
            "priority": "High",
        },
        {
            "project_id": "P-102",
            "name": "Website redesign",
            "status": "Active",
            "domain": "UI/UX",
        },
        {
            "project_id": "P-103",
            "name": "Database optimization",
            "status": "Planned",
            "project_type": "Maintenance",
        },
    ]

    for payload in project_payloads:
        project = client.post("/projects/", json=payload).json()
        pid = project["id"]
        for i in range(2):
            note = {"content": f"Note {i + 1} for {payload['project_id']}"}
            client.post(f"/projects/{pid}/notes/", json=note)

    projects = client.get("/projects/").json()
    save_table(OUTPUT_DIR / "projects.csv", projects)

    notes: List[Dict] = []
    for proj in projects:
        notes.extend(client.get(f"/projects/{proj['id']}/notes/").json())
    if notes:
        save_table(OUTPUT_DIR / "notes.csv", notes)

    print(f"Data tables generated in {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
