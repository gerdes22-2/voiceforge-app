import os
import logging
from typing import Optional
from storage.adapters.base import StorageAdapter
from storage.adapters.local import LocalStorageAdapter
# from storage.adapters.s3 import S3StorageAdapter (To be implemented with aioboto3)

logger = logging.getLogger("backend.storage")

def get_storage_adapter() -> StorageAdapter:
    provider = os.getenv("STORAGE_PROVIDER", "local").lower()
    
    if provider == "minio" or provider == "s3":
        # Temporary fallback to local until aioboto3 is fully configured
        # return S3StorageAdapter(...) 
        logger.warning("S3 provider selected but using LocalStorage fallback for now")
        return LocalStorageAdapter(base_path="/tmp/voiceforge_storage")
    elif provider == "local":
        return LocalStorageAdapter(base_path="/tmp/voiceforge_storage")
    else:
        logger.error(f"Unknown storage provider: {provider}. Falling back to local.")
        return LocalStorageAdapter(base_path="/tmp/voiceforge_storage")

storage_service = get_storage_adapter()
