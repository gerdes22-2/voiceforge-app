# VoiceForge AI Studio - System Dependency Graph

This document provides the definitive system map for the entire VoiceForge architecture, outlining the flow of data, state, execution, and external integrations.

## Core System Architecture

```mermaid
graph TD
    %% External Actors
    Client[User Browser / Next.js]
    PublicAPI[External Integrations]

    %% API Layer (FastAPI)
    subgraph API Layer [Backend - FastAPI]
        Auth[Auth & RBAC]
        REST[REST API v1]
        FeatureFlag[Feature Flags]
        Audit[Audit Logger]
        Analytics[Analytics Service]
    end

    %% AI Orchestration (Gateway)
    subgraph Gateway [AI Orchestrator]
        DAG[Workflow Engine / DAGs]
        Scheduler[GPU Scheduler & Auto-Scaler]
        Registry[AI Capability Registry]
        Health[Model Health Monitor]
    end

    %% Message Broker
    subgraph Messaging
        RedisQueue[(Redis Celery Queues)]
        PubSub[WebSockets / SSE]
    end

    %% Execution Layer
    subgraph Workers [Celery Workers]
        CPUWorker[CPU Workers - Fast/IO]
        GPUWorker[GPU Workers - Audio Processing]
    end

    %% AI Integrations
    subgraph AI Providers [Pluggable AI Execution]
        LocalModel[Local PyTorch Models]
        RunPod[RunPod Serverless]
        HuggingFace[Hugging Face API]
    end

    %% Data Layer
    subgraph Persistence
        DB[(PostgreSQL)]
        AudioCache[(Audio Cache)]
        ObjectStore[(S3 / R2 Storage)]
    end

    %% --- Connections ---
    
    %% Ingress
    Client -->|HTTP/REST| REST
    Client -->|WS/SSE| PubSub
    PublicAPI -.->|Future HTTP| REST

    %% API to Gateway & DB
    REST --> Auth
    REST --> FeatureFlag
    REST --> Audit
    REST --> DB
    REST --> DAG
    REST --> Analytics

    %% Gateway Logic
    DAG --> Registry
    DAG --> AudioCache
    DAG --> Scheduler

    %% Queueing & Scaling
    Scheduler <-->|Monitors Depth & Scales| RedisQueue
    Scheduler --> Health

    %% Worker Execution
    RedisQueue --> CPUWorker
    RedisQueue --> GPUWorker

    %% Pluggable AI Routing
    GPUWorker --> LocalModel
    GPUWorker --> RunPod
    GPUWorker --> HuggingFace

    %% Storage & Caching
    LocalModel --> ObjectStore
    CPUWorker --> ObjectStore
    GPUWorker --> AudioCache

    %% Progress Updates
    GPUWorker --> DB
    GPUWorker --> PubSub
    CPUWorker --> PubSub
```

## Explanation of Subsystems

1. **API Layer**: Handles ingress, validates JWT tokens via `Auth`, checks `Feature Flags` before exposing new capabilities, and writes security events to `Audit`.
2. **Gateway**: The brain of the operation. `Workflow Engine (DAG)` resolves complex chains (Upload -> Separate -> Pitch -> Convert -> Mix -> Master). `Registry` picks the correct model provider, and `Scheduler` scales infrastructure dynamically and queues the tasks.
3. **Workers & Providers**: The stateless celery workers execute jobs. The `AI Providers` interface dictates whether the model is executed locally (bare metal PyTorch) or dispatched to an external API (RunPod, HuggingFace).
4. **Caching & Persistence**: Intermediate steps are stored in `AudioCache` to bypass redundant GPU processing. Final artifacts go to `S3 / R2`, with metadata in `PostgreSQL`.
5. **Real-time Feedback**: `WebSockets / SSE` provides the client with live feedback on pipeline progression without polling.
