# AGENTS Instructions

This repository hosts the **Agile Project Management API**. The service exposes REST endpoints for creating, listing, updating and deleting projects using FastAPI and SQLModel with a SQLite backend.

## Goals
- Provide a simple standalone API for agile project records.
- Maintain tests ensuring the CRUD endpoints and dataset helpers work.

## Development notes
- Source code lives in `pm-api/` and tests in `tests/`.
- After making changes, install dependencies and run tests:
  ```bash
  pip install -r pm-api/requirements.txt httpx pytest
  pytest -q
  ```
- Follow PEP8 style conventions and keep modules modular as shown.

