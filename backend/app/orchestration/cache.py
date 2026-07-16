import hashlib
import json
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.models.audio import AudioCache

class CacheManager:
    """
    Generates deterministic hashes for inputs/parameters to reuse previous processing results.
    """
    @staticmethod
    def generate_hash(task_type: str, input_params: Dict[str, Any]) -> str:
        # Sort keys to ensure consistent hashing
        param_str = json.dumps(input_params, sort_keys=True)
        raw_key = f"{task_type}:{param_str}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    async def get_cached_result(db: AsyncSession, hash_key: str) -> Optional[AudioCache]:
        query = select(AudioCache).where(
            AudioCache.hash_key == hash_key
        )
        result = await db.execute(query)
        cache_entry = result.scalar_one_or_none()
        
        if cache_entry:
            # Check expiry
            if cache_entry.expires_at and cache_entry.expires_at < datetime.now(timezone.utc):
                return None
            return cache_entry
            
        return None

    @staticmethod
    async def store_cache_result(db: AsyncSession, task_type: str, input_params: Dict[str, Any], output_urls: Dict[str, str], expires_at: Optional[datetime] = None):
        hash_key = CacheManager.generate_hash(task_type, input_params)
        
        # In a real scenario, we might store multiple outputs (e.g. vocals, instrumental)
        # We can store them as JSON in a single Cache record, or individual records.
        # For AudioCache model as currently defined, it expects a single file_url.
        # We can adapt to store the main file or serialized dict.
        
        cache_entry = AudioCache(
            hash_key=hash_key,
            artifact_type=task_type,
            file_url=json.dumps(output_urls), # Storing dict as JSON string here for flexibility
            generation_params=input_params,
            expires_at=expires_at
        )
        db.add(cache_entry)
        await db.commit()
