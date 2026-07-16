# VoiceForge AI Studio - Repository Structure

```text
/
├── client/              # Next.js 15 Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/  # ShadCN UI & custom components
│   │   ├── hooks/       # React hooks (TanStack Query, WebSocket)
│   │   ├── lib/         # Utility functions, API clients
│   │   └── types/       # TypeScript shared interfaces
├── backend/             # FastAPI Business Logic
│   ├── app/
│   │   ├── api/v1/      # Versioned API routes
│   │   ├── core/        # Configuration, auth, security
│   │   ├── models/      # SQLAlchemy database models
│   │   └── schemas/     # Pydantic models (validation)
│   └── services/
│       ├── billing/     # Cost monitoring & usage tracking
│       ├── audit/       # Audit logging for user actions
│       ├── analytics/   # System metrics & telemetry
│       └── notifications/ # Email & Push Notifications
├── gateway/             # AI Orchestrator
│   ├── workflow/        # DAG Workflow Engine (Chained jobs)
│   ├── scheduler/       # GPU Scheduler & Auto-Scaler
│   └── registry/        # AI Capability Registry & Health Monitor
├── worker/              # Celery Workers (Stateless)
│   ├── tasks/           # Async task definitions
│   └── utils/           # Worker helper functions
├── ai/                  # AI Pipeline & Plugins
│   ├── models/          # Model adapters/interfaces
│   ├── providers/       # Pluggable execution (HuggingFace, RunPod, Local)
│   ├── services/        # Specific capability implementations
│   └── utils/           # Audio/Math processing utilities
├── storage/             # Storage Abstraction Layer
│   ├── adapters/        # S3, Local, R2 implementations
│   └── cache/           # Intermediate Audio Cache (Stems, Features)
├── shared/              # Shared libraries across services
│   ├── constants/
│   ├── logging/
│   └── utils/
├── docker/              # Infrastructure configs
├── docs/                # Architecture documentation
├── tests/               # Unit, Integration, E2E tests
│   ├── audio_qa/        # Objective audio metric tests (SNR, PESQ)
└── .env.example
```
