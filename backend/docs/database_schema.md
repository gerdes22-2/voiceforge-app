# VoiceForge Database Schema

This document outlines the production database layer for VoiceForge, implemented using SQLAlchemy 2.x and Alembic.

## Base Architecture
All primary tables inherit from:
- `Base`: SQLAlchemy Declarative Base
- `UUIDMixin`: Provides a time-sortable `UUIDv7` primary key (`id`).
- `TimestampMixin`: Provides timezone-aware `created_at` and `updated_at` timestamps.
- `SoftDeleteMixin`: Provides a `deleted_at` timestamp for non-destructive deletes (where appropriate).

## Core Entities

### 1. User
- **Description:** Represents a platform user.
- **Fields:** `email`, `password_hash`, `role` (Enum), `profile_data` (JSON).
- **Indexes:** `email` (Unique).
- **Relationships:** `projects`, `voice_datasets`, `voice_models`, `usage_logs`, `audit_logs`, `notifications`.

### 2. Project
- **Description:** Groups songs and models into a single workspace.
- **Fields:** `user_id`, `name`, `description`.
- **Indexes:** `user_id`.
- **Relationships:** `user`, `songs`.

### 3. Song
- **Description:** Represents an uploaded audio track to be processed.
- **Fields:** `project_id`, `original_file_uuid`, `title`, `status`, `metadata_info` (JSON).
- **Indexes:** `project_id`, `original_file_uuid`.
- **Relationships:** `project`, `processing_jobs`.

### 4. AudioCache
- **Description:** Caches intermediate audio artifacts to save redundant processing.
- **Fields:** `hash_key`, `artifact_type`, `file_url`, `generation_params` (JSON), `expires_at`.
- **Indexes:** `hash_key` (Unique), `expires_at`.

## Voice & Dataset Versioning

To ensure reproducibility and history, voice datasets are versioned.

### 5. VoiceDataset
- **Description:** A collection of audio samples for a specific voice.
- **Relationships:** `user`, `versions` (VoiceDatasetVersion).

### 6. VoiceDatasetVersion
- **Description:** An immutable snapshot of a VoiceDataset.
- **Fields:** `dataset_id`, `version_tag`, `file_uuids` (JSON), `total_duration_sec`, `quality_score`.
- **Relationships:** `dataset`, `voice_models`.

### 7. VoiceModel
- **Description:** A trained AI Voice Model derived from a dataset version.
- **Fields:** `user_id`, `dataset_version_id`, `name`, `provider_type`, `status`, `file_url`, `training_metrics` (JSON).
- **Relationships:** `user`, `dataset_version`, `training_jobs`.

## Jobs & Benchmarks

### 8. ProcessingJob
- **Description:** Tracks inference and processing tasks (e.g., Stem Separation).
- **Fields:** `song_id`, `task_type` (Enum), `status` (Enum), `progress`, `worker_id`, `error_message`, `result_data` (JSON).
- **Indexes:** Composite index on `(song_id, status)`.

### 9. TrainingJob
- **Description:** Tracks voice model training tasks.
- **Fields:** `voice_model_id`, `status` (Enum), `progress`, `worker_id`, `epochs_target`, `epochs_completed`, `error_message`.

### 10. JobBenchmark
- **Description:** Records detailed telemetry, performance, and quality metrics for jobs.
- **Fields:** `processing_job_id`, `training_job_id`, `provider_used`, `model_version`, `runtime_seconds`, `gpu_model`, `vram_used_mb`, `quality_score` (JSON), `processing_cost_est`, `output_durations` (JSON), `sample_rate`, `fallback_attempts`.
- **Performance:** Optimized for querying provider performance and tuning system heuristics.

### 11. Export
- **Description:** Tracks generated files available for user download.
- **Fields:** `job_id`, `format`, `file_url`.

## System & Infrastructure

### 12. Settings
- **Description:** Global application configuration stored in DB.
- **Fields:** `key` (Unique Index), `value` (JSON), `description`.

### 13. FeatureFlag
- **Description:** Toggles for new features and gradual rollouts.
- **Fields:** `key` (Unique Index), `is_enabled`, `rollout_percentage`.

### 14. ProviderRegistry
- **Description:** Registered AI capabilities and orchestrators (e.g. Demucs, RVC).
- **Fields:** `name` (Unique Index), `is_active`, `supported_task_types` (JSON).

### 15. ModelRegistry
- **Description:** Metadata for specific model versions.
- **Fields:** `name` (Unique Index), `description`, `version`.

### 16. AIModel
- **Description:** Specific AI model instantiations deployed to workers.
- **Fields:** `provider_id`, `registry_id`, `is_active`, `memory_req_mb`.

### 17. GPUWorker
- **Description:** Tracks active background workers.
- **Fields:** `hostname`, `gpu_type`, `vram_total`, `status`, `last_heartbeat`.

### 18. JobQueueMetric
- **Description:** Periodic snapshots of queue health.
- **Fields:** `queue_name` (Index), `pending_count`, `active_count`, `avg_wait_time_sec`.

## Logging & Auditing

### 19. UsageLog
- **Description:** Billing and quota tracking for compute usage.
- **Fields:** `user_id`, `job_id`, `gpu_seconds`, `cpu_seconds`, `storage_bytes`.

### 20. AuditLog
- **Description:** Security and compliance events.
- **Fields:** `user_id`, `action` (Index), `resource_type`, `resource_id`, `ip_address`, `metadata_info` (JSON).

### 21. Notification
- **Description:** User alerts (e.g., job completed).
- **Fields:** `user_id`, `type`, `title`, `message`, `is_read`, `action_url`.

## Migration Operations
- Generate new migrations using: `./backend/generate_migration.sh "Description"`
- Test migration application and rollback using: `./backend/test_migration.sh`
