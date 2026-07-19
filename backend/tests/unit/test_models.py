import pytest
import uuid
from datetime import datetime, timezone
from app.models import (
    User, Project, Song, AudioCache, VoiceDataset, VoiceDatasetVersion,
    VoiceModel, ProcessingJob, TrainingJob, JobBenchmark, Export,
    Settings, FeatureFlag, ProviderRegistry, ModelRegistry, AIModel, GPUWorker,
    JobQueueMetric, UsageLog, AuditLog, Notification
)
from app.models.enums import UserRole, JobStatus, JobType

def test_user_model_instantiation():
    user = User(email="test@example.com", password_hash="hash", role=UserRole.ADMIN)
    assert user.email == "test@example.com"
    assert user.role == UserRole.ADMIN

def test_project_model_instantiation():
    u_id = uuid.uuid4()
    project = Project(user_id=u_id, name="Test Project")
    assert project.user_id == u_id
    assert project.name == "Test Project"

def test_song_model_instantiation():
    p_id = uuid.uuid4()
    file_id = uuid.uuid4()
    song = Song(project_id=p_id, original_file_uuid=file_id, title="Test Song")
    assert song.project_id == p_id
    assert song.status == "uploaded"

def test_job_benchmark_instantiation():
    j_id = uuid.uuid4()
    benchmark = JobBenchmark(
        processing_job_id=j_id,
        provider_used="demucs",
        model_version="v4",
        runtime_seconds=120.5,
        gpu_model="RTX 4090",
        vram_used_mb=4096,
        quality_score={"confidence": 0.95},
        processing_cost_est=0.02,
        output_durations={"vocals": 180},
        sample_rate=44100,
        fallback_attempts=1
    )
    assert benchmark.provider_used == "demucs"
    assert benchmark.runtime_seconds == 120.5
    assert benchmark.vram_used_mb == 4096
    assert benchmark.quality_score["confidence"] == 0.95

def test_dataset_versioning_instantiation():
    u_id = uuid.uuid4()
    dataset = VoiceDataset(user_id=u_id, name="My Voice")
    d_id = uuid.uuid4()
    version = VoiceDatasetVersion(dataset_id=d_id, version_tag="v1.0", file_uuids=["file1", "file2"])
    
    assert dataset.name == "My Voice"
    assert version.version_tag == "v1.0"
    assert "file1" in version.file_uuids

def test_timestamp_and_soft_delete():
    user = User(email="test2@example.com", password_hash="hash")
    # Base attributes shouldn't be initialized automatically without DB session,
    # but we can check if the columns exist on the class
    assert hasattr(User, "created_at")
    assert hasattr(User, "updated_at")
    assert hasattr(User, "deleted_at")
