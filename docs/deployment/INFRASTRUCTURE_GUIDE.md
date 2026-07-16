# VoiceForge AI Studio - Deployment Guide

This document provides instructions for deploying the VoiceForge AI Studio platform to production using managed platforms (Render/Railway), GPU serverless platforms (RunPod), and Object Storage (Cloudflare R2/AWS S3).

## 1. Web Services (Frontend, Backend, Gateway)
**Recommended Platform**: Render or Railway

### Configuration
1. Connect your GitHub repository to Render/Railway.
2. Create separate services for:
   - **Frontend**: Root Directory `client/`, Build Command `npm run build`, Start Command `npm start`.
   - **Backend**: Root Directory `backend/`, Docker deployment.
   - **Gateway**: Root Directory `gateway/`, Docker deployment.

### Environment Variables
Configure the following in the platform's environment settings:
- `DATABASE_URL`: Managed PostgreSQL connection string.
- `REDIS_URL`: Managed Redis connection string.
- `JWT_SECRET`: Generate a secure random string.
- `STORAGE_PROVIDER`: `s3` (for production).

## 2. GPU Workers (Celery & AI Models)
**Recommended Platform**: RunPod (Serverless or Pods)

### Serverless Endpoint Deployment
1. Build the `ai/Dockerfile` and push to Docker Hub or AWS ECR.
2. In RunPod, create a new Serverless Endpoint.
3. Select your pushed Docker image.
4. Choose appropriate GPU tiers (e.g., RTX 4090 or A100 based on VRAM needs).
5. Set environment variables (Object Storage Keys, RunPod API Key).

### Stateful Worker Deployment
1. Build the `worker/Dockerfile` and push to a registry.
2. Deploy as a RunPod Pod with persistent volume attached.
3. Supply `CELERY_BROKER_URL` and `DATABASE_URL` so the worker can connect to the primary cluster.

## 3. Object Storage
**Recommended Platform**: Cloudflare R2 or AWS S3

1. Create a Bucket (e.g., `voiceforge-prod`).
2. Configure CORS to allow your frontend domain if direct uploads are utilized.
3. Generate Access Keys.
4. Set `S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET_NAME`, and `S3_REGION` in the Backend, Gateway, and Worker environments.

## 4. Networking & CORS
- Ensure `BACKEND_CORS_ORIGINS` includes the production frontend URL (e.g., `https://voiceforge.ai`).
- Ensure internal services (Gateway, Backend) can communicate via private networking if hosted on the same provider (e.g., Render Private Network).

## 5. Local Validation & Development Setup
For new developers onboarding:
```bash
# 1. Clone repository
git clone https://github.com/your-org/voiceforge.git
cd voiceforge

# 2. Setup environment variables
cp .env.example .env

# 3. Start the entire stack
docker-compose up -d --build

# 4. Verify services are running
docker-compose ps
```
Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Gateway: http://localhost:8080
- MinIO Console: http://localhost:9001
