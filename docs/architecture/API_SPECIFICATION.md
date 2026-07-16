# VoiceForge AI Studio - REST API Specification (/api/v1)

## Base URL
`/api/v1`

## Authentication
JWT required for all endpoints.

## Endpoints

### Auth
- `POST /auth/login`
- `POST /auth/register`
- `POST /auth/refresh`

### Public API (Reserved for future external integrations)
- `POST /public/projects`
- `POST /public/songs`
- `POST /public/workflows`

### System & Config
- `GET /features` (Retrieve active feature flags)
- `GET /metrics` (Analytics and system health)

### Projects
- `GET /projects`
- `POST /projects`
- `GET /projects/{project_id}`

### Songs
- `POST /songs` (Upload)
- `GET /songs/{song_id}/status`

### AI Jobs
- `POST /jobs` (Enqueue job)
- `GET /jobs/{job_id}/progress` (Legacy fallback)
- `GET /jobs/stream` (SSE/WebSocket connection for real-time progress updates across all active jobs)

### Billing & Usage
- `GET /usage` (Retrieve current billing cycle usage metrics)
- `GET /usage/history` (Retrieve historical usage)
