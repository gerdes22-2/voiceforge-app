FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN touch requirements.txt && pip install --no-cache-dir -r requirements.txt

RUN addgroup --system aigroup && adduser --system --group aiuser
COPY . .
RUN chown -R aiuser:aigroup /app
USER aiuser

EXPOSE 8001
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:8001/health || exit 1

CMD ["uvicorn", "services.main:app", "--host", "0.0.0.0", "--port", "8001"]
