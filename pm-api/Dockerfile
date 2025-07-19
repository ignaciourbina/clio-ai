# ---- Dockerfile ------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# 1) Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy the rest of the project
COPY . .

# 3) Launch FastAPI on HF’s default port 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
