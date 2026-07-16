from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class StorageAdapter(ABC):
    @abstractmethod
    async def upload(self, file_obj: BinaryIO, destination_path: str, content_type: str) -> str:
        """Uploads a file and returns the remote path or URL."""
        pass

    @abstractmethod
    async def download(self, remote_path: str, local_path: str) -> None:
        """Downloads a file from storage to the local filesystem."""
        pass

    @abstractmethod
    async def get_url(self, remote_path: str, expires_in: int = 3600) -> str:
        """Returns a signed or public URL to access the file."""
        pass

    @abstractmethod
    async def delete(self, remote_path: str) -> bool:
        """Deletes a file from storage."""
        pass
