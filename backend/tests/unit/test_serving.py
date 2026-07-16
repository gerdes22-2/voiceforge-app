import pytest
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
