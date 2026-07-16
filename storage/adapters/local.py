import os
import shutil
import aiofiles
from typing import BinaryIO
from .base import StorageAdapter

class LocalStorageAdapter(StorageAdapter):
    def __init__(self, base_path: str = "/tmp/voiceforge_storage"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def upload(self, file_obj: BinaryIO, destination_path: str, content_type: str) -> str:
        full_path = os.path.join(self.base_path, destination_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Read/write chunk by chunk for safety
        async with aiofiles.open(full_path, 'wb') as out_file:
            while content := file_obj.read(1024 * 1024):  # 1MB chunks
                await out_file.write(content)
                
        return destination_path

    async def download(self, remote_path: str, local_path: str) -> None:
        full_path = os.path.join(self.base_path, remote_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")
            
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        async with aiofiles.open(full_path, 'rb') as in_file:
            async with aiofiles.open(local_path, 'wb') as out_file:
                while content := await in_file.read(1024 * 1024):
                    await out_file.write(content)

    async def get_url(self, remote_path: str, expires_in: int = 3600) -> str:
        # In a real local setup, this would point to a local file serving route in FastAPI
        return f"/files/{remote_path}"

    async def delete(self, remote_path: str) -> bool:
        full_path = os.path.join(self.base_path, remote_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
