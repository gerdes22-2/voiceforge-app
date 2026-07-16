FROM python:3.11-slim
WORKDIR /app
COPY worker/requirements.txt .
COPY shared/requirements.txt shared-reqs.txt
RUN pip install --no-cache-dir -r requirements.txt -r shared-reqs.txt
COPY shared/ shared/
COPY worker/ worker/
WORKDIR /app/worker
CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info"]
