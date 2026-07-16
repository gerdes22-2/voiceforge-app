import pytest
from app.orchestration.cache import CacheManager
from app.models.workflow import TaskState

def test_cache_hash_consistency():
    task_type = "stem_separation"
    params1 = {"model": "htdemucs", "shift": 1}
    params2 = {"shift": 1, "model": "htdemucs"}
    
    hash1 = CacheManager.generate_hash(task_type, params1)
    hash2 = CacheManager.generate_hash(task_type, params2)
    
    assert hash1 == hash2

def test_task_state_enum():
    assert TaskState.PENDING == "pending"
    assert TaskState.COMPLETED == "completed"
