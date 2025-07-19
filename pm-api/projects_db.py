"""projects_db.py – **Data‑layer module** for the Agile Project Management API
=============================================================================

This file owns every concern related to *persistence* so that the rest of the
application (see ``app.py``) can remain a thin HTTP façade.

Key responsibilities
--------------------
1. **Locate or create a writable SQLite file**
2. **Expose a configured SQLModel ``engine``**
3. Declare core **table‑models** – **Project** – with helpful defaults and indexes.
4. Provide a single, idempotent **``init_db()``** helper that the FastAPI
   lifespan event can call exactly once on startup.

Developer log
-------------
* **v1.2.1 (2025‑07‑17)** – Switched default DB directory to */tmp/agile_data*
  to avoid container write‑permission issues.
* **v1.2.0 (2025‑07‑17)** – Removed ``Ticket`` table; added richer Project fields.
* **v1.1.0 (2025‑07‑17)** – Added ``created_at``/``updated_at`` auto‑timestamps.
* **v1.0.0 (2025‑07‑17)** – First public release extracted from monolith.

Usage
-----
```python
from projects_db import engine, init_db, Project
from sqlmodel import Session

init_db()

with Session(engine) as sess:
    proj = Project(project_id="P012", name="Refactor search", status="Active")
    sess.add(proj)
    sess.commit()
```
"""

from __future__ import annotations

import os
import datetime as _dt
from pathlib import Path
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine

# --------------------------------------------------------------------------- #
# 1. Resolve a safe absolute path for the SQLite file
# --------------------------------------------------------------------------- #
# Default location is /tmp/agile_data (writable in most containers). Override
# either directory or filename with env‑vars DB_DIR / DB_FILE.
# --------------------------------------------------------------------------- #

_DB_DIR = Path(os.getenv("DB_DIR", "/tmp/agile_data")).expanduser().resolve()
_DB_DIR.mkdir(parents=True, exist_ok=True)

_DB_FILE = _DB_DIR / os.getenv("DB_FILE", "pipeline.db")

# Four leading slashes after ``sqlite:`` → absolute POSIX path.
DATABASE_URL: str = f"sqlite:///{_DB_FILE.as_posix()}"

# Exported SQLAlchemy / SQLModel engine – importable by other modules.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

# --------------------------------------------------------------------------- #
# 2. Table models
# --------------------------------------------------------------------------- #

class _UTCDateTime(SQLModel, table=False):
    """Mixin providing UTC ``created_at`` / ``updated_at`` columns."""

    created_at: _dt.datetime = Field(
        default_factory=_dt.datetime.utcnow, nullable=False, description="UTC when row was created"
    )
    updated_at: _dt.datetime = Field(
        default_factory=_dt.datetime.utcnow, nullable=False, description="UTC when row was last modified"
    )


class Project(_UTCDateTime, table=True):
    """Represents a high‑level project in an agile board."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Identifiers & metadata
    project_id: str = Field(index=True, unique=True, nullable=False, description="Human‑friendly code, e.g. P‑101")
    name: str = Field(nullable=False, description="Project title")
    description: Optional[str] = Field(default=None, description="Free‑form details / scope notes")

    status: str = Field(default="Planned", description="Status label (Planned / Active / Done / On‑Hold)")
    priority: Optional[str] = Field(default="Medium", description="High / Medium / Low")
    domain: Optional[str] = Field(default=None, description="Business domain / area owner")

    # Rich fields
    next_steps: Optional[str] = Field(default=None, description="Immediate next actions / blockers")
    deadline: Optional[_dt.date] = Field(default=None, description="Target completion date (UTC)")
    project_type: Optional[str] = Field(default=None, description="Epic / Feature / Maintenance / ...")
    tooling: Optional[str] = Field(default=None, description="Stack or primary tools in use")

# --------------------------------------------------------------------------- #
# 3. Schema initialisation helper
# --------------------------------------------------------------------------- #

def init_db() -> None:
    """Create the Project table *if* it doesn’t already exist."""

    _DB_DIR.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)


# Convenience: run ``python projects_db.py`` for a one‑off init.
if __name__ == "__main__":
    print(f"Initialising database at {_DB_FILE} …", flush=True)
    init_db()
    print("Done ✔", flush=True)
