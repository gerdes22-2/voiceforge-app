FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc python3-dev && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt backend-reqs.txt
COPY worker/requirements.txt worker-reqs.txt
COPY shared/requirements.txt shared-reqs.txt
RUN pip install --no-cache-dir -r backend-reqs.txt -r worker-reqs.txt -r shared-reqs.txt
COPY shared/ shared/
COPY worker/ worker/
COPY backend/ backend/
WORKDIR /app/backend

# We will use a script to run both Celery and FastAPI to stay on Render's free tier
COPY backend/start.sh .
RUN chmod +x start.sh
CMD ["./start.sh"]
