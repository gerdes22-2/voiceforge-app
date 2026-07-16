FROM python:3.11-slim
WORKDIR /app
COPY gateway/requirements.txt .
COPY shared/requirements.txt shared-reqs.txt
RUN pip install --no-cache-dir -r requirements.txt -r shared-reqs.txt
COPY shared/ shared/
COPY gateway/ gateway/
WORKDIR /app/gateway
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
