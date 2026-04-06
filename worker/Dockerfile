FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install worker requirements
COPY worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# We copy the entire root so the worker can import backend models and strategies.
# In a real monorepo, backend/app would be a shared library, but for this demo,
# setting PYTHONPATH=/app and copying both works perfectly.
COPY backend/app /app/app
COPY worker/app /app/worker_app

CMD ["python", "worker_app/main.py"]
