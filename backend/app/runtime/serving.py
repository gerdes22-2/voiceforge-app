from typing import Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class GPUMemoryManager:
    """
    Tracks and allocates GPU VRAM globally across the node to prevent OOM errors.
    """
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
    """
    Centralized registry and loader for Voice Models on a worker.
    Prevents redundant loading of the same model and manages VRAM limits.
    """
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
