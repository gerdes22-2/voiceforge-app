import os

with open("backend/app/runtime/serving.py", "w") as f:
    f.write("""from typing import Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class GPUMemoryManager:
    \"\"\"
    Tracks and allocates GPU VRAM globally across the node to prevent OOM errors.
    \"\"\"
    _total_vram_mb = 24000 # Mock 24GB node
    _allocated_vram_mb = 0
    _lock = asyncio.Lock()
    
    @classmethod
    async def allocate(cls, mb: int) -> bool:
        async with cls._lock:
            if cls._allocated_vram_mb + mb <= cls._total_vram_mb:
                cls._allocated_vram_mb += mb
                logger.info(f"Allocated {mb}MB VRAM. Total used: {cls._allocated_vram_mb}MB / {cls._total_vram_mb}MB")
                return True
            logger.warning(f"Failed to allocate {mb}MB VRAM. Total used: {cls._allocated_vram_mb}MB / {cls._total_vram_mb}MB")
            return False
            
    @classmethod
    async def release(cls, mb: int):
        async with cls._lock:
            cls._allocated_vram_mb = max(0, cls._allocated_vram_mb - mb)
            logger.info(f"Released {mb}MB VRAM. Total used: {cls._allocated_vram_mb}MB / {cls._total_vram_mb}MB")

class VoiceModelServer:
    \"\"\"
    Centralized registry and loader for Voice Models on a worker.
    Prevents redundant loading of the same model and manages VRAM limits.
    \"\"\"
    _loaded_models: Dict[str, Any] = {}
    _model_locks: Dict[str, asyncio.Lock] = {}
    
    @classmethod
    async def load_model(cls, model_id: str, vram_required_mb: int = 4000) -> Any:
        if model_id not in cls._model_locks:
            cls._model_locks[model_id] = asyncio.Lock()
            
        async with cls._model_locks[model_id]:
            if model_id in cls._loaded_models:
                logger.info(f"Model {model_id} already loaded in VRAM.")
                return cls._loaded_models[model_id]
                
            logger.info(f"Loading model {model_id} into VRAM...")
            
            if not await GPUMemoryManager.allocate(vram_required_mb):
                raise MemoryError(f"Insufficient VRAM to load model {model_id}")
                
            # Mock loading process
            await asyncio.sleep(0.1) 
            cls._loaded_models[model_id] = {
                "id": model_id, 
                "status": "loaded", 
                "vram_mb": vram_required_mb,
                "weights": "mock_tensor_data"
            }
            logger.info(f"Model {model_id} successfully loaded.")
            return cls._loaded_models[model_id]
            
    @classmethod
    async def unload_model(cls, model_id: str):
        if model_id not in cls._model_locks:
            return
            
        async with cls._model_locks[model_id]:
            if model_id in cls._loaded_models:
                vram_freed = cls._loaded_models[model_id]["vram_mb"]
                del cls._loaded_models[model_id]
                await GPUMemoryManager.release(vram_freed)
                logger.info(f"Unloaded model {model_id}.")
""")

# Test for serving layer
with open("backend/tests/unit/test_serving.py", "w") as f:
    f.write("""import pytest
import asyncio
from app.runtime.serving import GPUMemoryManager, VoiceModelServer

@pytest.mark.asyncio
async def test_gpu_memory_allocation():
    # Reset for test
    GPUMemoryManager._allocated_vram_mb = 0
    
    success = await GPUMemoryManager.allocate(4000)
    assert success is True
    assert GPUMemoryManager._allocated_vram_mb == 4000
    
    # Try to allocate more than available (assuming 24000 total)
    success = await GPUMemoryManager.allocate(25000)
    assert success is False
    assert GPUMemoryManager._allocated_vram_mb == 4000
    
    await GPUMemoryManager.release(4000)
    assert GPUMemoryManager._allocated_vram_mb == 0

@pytest.mark.asyncio
async def test_voice_model_server():
    # Reset
    GPUMemoryManager._allocated_vram_mb = 0
    VoiceModelServer._loaded_models.clear()
    
    model_id = "test_model_1"
    
    # Initial load
    model = await VoiceModelServer.load_model(model_id, vram_required_mb=4000)
    assert model["id"] == model_id
    assert GPUMemoryManager._allocated_vram_mb == 4000
    
    # Second load should reuse
    model2 = await VoiceModelServer.load_model(model_id, vram_required_mb=4000)
    assert model2 is model
    assert GPUMemoryManager._allocated_vram_mb == 4000 # Still 4000
    
    # Unload
    await VoiceModelServer.unload_model(model_id)
    assert model_id not in VoiceModelServer._loaded_models
    assert GPUMemoryManager._allocated_vram_mb == 0
""")
