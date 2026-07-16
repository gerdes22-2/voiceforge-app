# AI Orchestration Layer

The AI Orchestration Layer is the heart of VoiceForge's processing capabilities. It acts as a control plane for managing complex, multi-step AI jobs.

## Core Capabilities
- **Workflow Engine (DAG)**: Defines tasks as Directed Acyclic Graphs, ensuring steps execute in the correct order based on dependencies.
- **Job Lifecycle Management**: Tracks state transitions (Pending -> Queued -> Running -> Completed/Failed). Emits events to the immutable Project Timeline.
- **Intelligent Scheduler**: Determines whether a task needs a GPU or CPU and dispatches it to the appropriate worker queue (Celery/RQ mocked for now).
- **Artifact Manager**: Treats every output (e.g., isolated stems, pitch maps) as a reusable `FileAsset`.
- **Cache Manager**: Hashes task parameters deterministically. If an exact match is found, the previous result is reused, saving compute time.
- **Retry & Cancellation**: Supports max retries with backoff. Workflows can be gracefully cancelled mid-execution, cascading cancellation to all non-terminal tasks.
- **Resumable Workflows**: If a workflow fails midway (e.g., during Voice Conversion), it can be resumed. The engine skips previously COMPLETED nodes and picks up right where it left off.
- **Metrics Collection**: Tracks queue times, active jobs, and failure rates to optimize worker scaling.

## Data Structures
- `Workflow`: Groups tasks together (e.g., "Full Vocal Processing").
- `WorkflowTask`: Individual DAG node (e.g., `stem_separation`).

## Execution Flow
1. User requests a process (e.g. via `POST /api/v1/workflows`).
2. `WorkflowBuilder` constructs the DAG and persists it.
3. `WorkflowEngine` scans for `PENDING` tasks with zero unresolved dependencies and marks them runnable.
4. `Scheduler` dispatches runnable tasks to the worker queues.
5. External workers pick up tasks, update `progress`, and output artifacts via `ArtifactManager`.
6. State changes trigger further evaluation of the DAG.
