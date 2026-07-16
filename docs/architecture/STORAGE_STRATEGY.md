# VoiceForge AI Studio - Storage Strategy

We use an abstraction layer defined in `storage/adapters/`.

```python
class StorageAdapter(ABC):
    @abstractmethod
    def upload(self, local_path: str, remote_path: str): pass
    @abstractmethod
    def download(self, remote_path: str, local_path: str): pass
```

Implementations exist for:
- `LocalStorageAdapter` (Dev)
- `S3StorageAdapter` (Prod)
