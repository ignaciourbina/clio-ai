"""
app.py – FastAPI layer for the **Agile Project Management API**
==============================================================

Developer log
-------------
* **v2.0.0 (2025–07–17)** – **Pruned Ticket subsystem**; file now focuses on
  Project CRUD only and adopts richer project fields.
* **v1.0.1 (2025–07–17)** – Added rich top‑level docstring, expanded inline
  commentary, clarified exception semantics and HTTP responses, and renamed a
  few helper variables for readability.
* **v1.0.0 (2025–07–17)** – First modular cut extracted from legacy monolith;
  data‑layer moved to ``projects_db.py``; CRUD for projects & tickets; API‑key
  security; SQLite persistence.

Purpose & architecture
----------------------
This file contains *only* HTTP‑facing concerns for **projects**:

* Defines a **FastAPI** application object discovered automatically by Uvicorn.
* Performs **API‑key** validation on every request via a global dependency.
* Delegates all persistence to :pyfile:`projects_db.py`, which exports the
  SQLModel ``engine`` and table model ``Project`` plus the ``init_db()`` helper.
* Uses a **lifespan** context instead of deprecated ``@app.on_event`` hooks so
  tables are created exactly once at startup regardless of workers.

If you need to extend behaviour (e.g. labels, sprints), add new table models to
*projects_db.py* and new routers here – the pattern is already shown.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Standard‑library imports
# --------------------------------------------------------------------------- #

import os
import datetime
from typing import List, Optional, AsyncGenerator, Iterator
from contextlib import asynccontextmanager

# --------------------------------------------------------------------------- #
# Third‑party imports – FastAPI, SQLModel, etc.
# --------------------------------------------------------------------------- #

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import FileResponse, JSONResponse
import base64
from sqlmodel import Session, select
from pydantic import BaseModel

import projects_db as db  # local data‑layer (keeps this module lean)

# --------------------------------------------------------------------------- #
# Security – simple *header‑based* API‑key auth
# --------------------------------------------------------------------------- #

API_KEY: str = os.getenv("API_KEY", "CHANGE_ME")  # ‼️ override in env‑vars ❗
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    """Raise *401 Unauthorized* if header missing or mismatch."""
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API Key",
        headers={"WWW-Authenticate": "API Key"},
    )

# --------------------------------------------------------------------------- #
# FastAPI app factory – lifespan initialises the DB once per process
# --------------------------------------------------------------------------- #

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create tables if absent, then yield control to the server runtime."""
    db.init_db()  # idempotent – safe to call every boot
    yield

app = FastAPI(
    title="Agile Project Management API",
    description="Manage projects via REST",
    version="2.0.0",
    lifespan=lifespan,
    dependencies=[Depends(get_api_key)],  # global – applies to all routes
)

# --------------------------------------------------------------------------- #
# Pydantic payload models – wrappers around incoming JSON bodies
# --------------------------------------------------------------------------- #

class ProjectIn(BaseModel):
    """*Input* schema for **create** project."""

    project_id: str
    name: str
    status: str = "Planned"  # Planned | Active | Done | On‑Hold
    next_steps: Optional[str] = None
    deadline: Optional[datetime.date] = None
    project_type: Optional[str] = None
    domain: Optional[str] = None
    tooling: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    """Payload for **partial update** (PUT) – all fields optional."""

    name: Optional[str] = None
    status: Optional[str] = None
    next_steps: Optional[str] = None
    deadline: Optional[datetime.date] = None
    project_type: Optional[str] = None
    domain: Optional[str] = None
    tooling: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None


class NoteIn(BaseModel):
    """Input schema for creating a project note."""

    content: str


class NoteUpdate(BaseModel):
    """Payload for updating a project note."""

    content: Optional[str] = None

# --------------------------------------------------------------------------- #
# Dependency – generator yields a *scoped* SQLModel session per request
# --------------------------------------------------------------------------- #

def get_session() -> Iterator[Session]:
    """Provide a scoped SQLModel session and close it automatically."""
    with Session(db.engine) as session:
        yield session

# --------------------------------------------------------------------------- #
# Project routes – CRUD ops
# --------------------------------------------------------------------------- #

@app.post("/projects/", response_model=db.Project, status_code=201)
def create_project(payload: ProjectIn, session: Session = Depends(get_session)):
    """Insert a new *Project* row and return the persisted object."""
    project = db.Project(**payload.dict())
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@app.get("/projects/", response_model=List[db.Project])
def list_projects(session: Session = Depends(get_session)):
    """Return **all** projects – future work: add query params for filtering."""
    return session.exec(select(db.Project)).all()

@app.get("/projects/{project_id}", response_model=db.Project)
def get_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(db.Project, project_id)
    if not project:
        raise HTTPException(404, f"Project {project_id} not found")
    return project

@app.put("/projects/{project_id}", response_model=db.Project)
def update_project(project_id: int, upd: ProjectUpdate, session: Session = Depends(get_session)):
    project = session.get(db.Project, project_id)
    if not project:
        raise HTTPException(404, f"Project {project_id} not found")

    for field, value in upd.dict(exclude_unset=True).items():
        setattr(project, field, value)
    project.updated_at = datetime.datetime.utcnow()

    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@app.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(db.Project, project_id)
    if not project:
        raise HTTPException(404, f"Project {project_id} not found")
    session.delete(project)
    session.commit()

# --------------------------------------------------------------------------- #
# Project notes – simple notebook entries per project
# --------------------------------------------------------------------------- #

@app.post("/projects/{project_id}/notes/", response_model=db.ProjectNote, status_code=201)
def create_note(project_id: int, payload: NoteIn, session: Session = Depends(get_session)):
    if not session.get(db.Project, project_id):
        raise HTTPException(404, f"Project {project_id} not found")
    note = db.ProjectNote(project_id=project_id, content=payload.content)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

@app.get("/projects/{project_id}/notes/", response_model=List[db.ProjectNote])
def list_notes(project_id: int, session: Session = Depends(get_session)):
    if not session.get(db.Project, project_id):
        raise HTTPException(404, f"Project {project_id} not found")
    stmt = select(db.ProjectNote).where(db.ProjectNote.project_id == project_id)
    return session.exec(stmt).all()

@app.get("/notes/{note_id}", response_model=db.ProjectNote)
def get_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(db.ProjectNote, note_id)
    if not note:
        raise HTTPException(404, f"Note {note_id} not found")
    return note

@app.put("/notes/{note_id}", response_model=db.ProjectNote)
def update_note(note_id: int, upd: NoteUpdate, session: Session = Depends(get_session)):
    note = session.get(db.ProjectNote, note_id)
    if not note:
        raise HTTPException(404, f"Note {note_id} not found")
    for field, value in upd.dict(exclude_unset=True).items():
        setattr(note, field, value)
    note.updated_at = datetime.datetime.utcnow()
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(db.ProjectNote, note_id)
    if not note:
        raise HTTPException(404, f"Note {note_id} not found")
    session.delete(note)
    session.commit()

# --------------------------------------------------------------------------- #
# Dataset helpers – download / purge DB
# --------------------------------------------------------------------------- #

@app.get("/api/dataset", response_class=FileResponse)
def download_db():
    """Download the *raw* SQLite file for offline analysis/back‑ups."""
    return FileResponse(
        path=str(db._DB_FILE),
        filename="agile.db",
        media_type="application/octet-stream",
    )

@app.get("/api/dataset/raw", response_class=JSONResponse)
def download_db_raw() -> JSONResponse:
    """
    Download the *raw* SQLite file embedded in JSON (base64‑encoded).
    Clients receive {"filename": "...", "data": "<base64>"}.
    """
    # 1. Read raw bytes of the DB file
    with open(db._DB_FILE, "rb") as f:
        blob = f.read()

    # 2. Base64‑encode and decode to UTF‑8 for JSON serialization
    encoded = base64.b64encode(blob).decode("utf-8")

    # 3. Return as JSON
    return JSONResponse(
        content={
            "filename": db._DB_FILE.name,
            "data": encoded
        },
        media_type="application/json"
    )

@app.delete("/api/dataset", status_code=200)
def purge_db():
    """Delete DB file **irrevocably** and recreate an empty schema."""
    if os.path.exists(db._DB_FILE):
        os.remove(db._DB_FILE)
    db.init_db()
    return {"detail": "database reset; all projects purged"}

# --------------------------------------------------------------------------- #
# Misc – simple health check (suitable for /ready probe)
# --------------------------------------------------------------------------- #

@app.get("/")
def root():
    """Basic connectivity check – returns fixed JSON."""
    return {"message": "Agile Project Management API is running"}
