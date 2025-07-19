---
title: Pm Api
emoji: 🌖
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
short_description: PMing API
---


# Agile Project Management API – cURL Reference (Windows CMD)

All endpoints require the header **X-API-Key**.  
This version uses Windows CMD variables (`%BASE_URL%`, `%API_KEY%`).  
**Set these variables first:**

```cmd
set BASE_URL=http://localhost:8000
set API_KEY=CHANGE_ME
````

---

## Health Check

```cmd
curl -H "X-API-Key: %API_KEY%" "%BASE_URL%/"
```

---

## Project CRUD

### Create Project

```cmd
curl -X POST "%BASE_URL%/projects/" -H "X-API-Key: %API_KEY%" -H "Content-Type: application/json" -d "{\"project_id\":\"P-001\",\"name\":\"My First Project\",\"status\":\"Planned\",\"next_steps\":\"Kickoff soon\",\"deadline\":\"2025-08-01\",\"project_type\":\"Feature\",\"domain\":\"AI\",\"tooling\":\"Python,FastAPI\",\"priority\":\"High\",\"description\":\"Initial test project\"}"
```

### List All Projects

```cmd
curl -H "X-API-Key: %API_KEY%" "%BASE_URL%/projects/"
```

### Get Project by ID

```cmd
curl -H "X-API-Key: %API_KEY%" "%BASE_URL%/projects/1"
:: Replace 1 with the desired project integer ID
```

### Update Project (Partial/Full, by ID)

```cmd
curl -X PUT "%BASE_URL%/projects/1" -H "X-API-Key: %API_KEY%" -H "Content-Type: application/json" -d "{\"status\":\"Active\",\"priority\":\"Medium\",\"next_steps\":\"Sprint planning\"}"
:: Only include fields you want to update
:: Replace 1 with your project ID
```

### Delete Project by ID

```cmd
curl -X DELETE -H "X-API-Key: %API_KEY%" "%BASE_URL%/projects/1"
:: Replace 1 with your project ID
```

---

## Dataset Helpers

### Download DB File

```cmd
curl -O -J -H "X-API-Key: %API_KEY%" "%BASE_URL%/api/dataset"
```

### Download Raw DB as Base64 JSON

```cmd
curl -H "X-API-Key: %API_KEY%" "%BASE_URL%/api/dataset/raw"
```

### Purge (Reset) DB

```cmd
curl -X DELETE -H "X-API-Key: %API_KEY%" "%BASE_URL%/api/dataset"
```

---

## Notes

* **Set variables** first every time you open CMD:

  ```cmd
  set BASE_URL=http://localhost:8000
  set API_KEY=CHANGE_ME
  ```
* Or, replace `%BASE_URL%` and `%API_KEY%` directly in each command with your host and key.
* All JSON data must use escaped double quotes (`\"`) in CMD.
* For IDs, always use the integer primary key, not the string `project_id` field.
* OpenAPI docs available at: `%BASE_URL%/docs` (use **Authorize** button to enter API key).

---
