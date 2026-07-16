# VoiceForge AI Studio - AI Pipeline & Plugin Architecture

## Pipeline Flow
Frontend (API) -> Backend (Validate/Store) -> Gateway (AI Model Manager -> GPU Scheduler -> Orchestrate/Queue) -> Redis -> Worker (Run Job -> Audio Cache) -> AI Service (Adapter) -> Storage

## Gateway Services
1. **AI Model Manager & Capability Registry**: Dynamically selects the best AI plugin based on required capabilities (e.g., harmony generation, language support, sample rate) and current model health (avg runtime, failure rate). Unhealthy models are automatically disabled.
2. **GPU Scheduler & Auto-Scaler**: Routes jobs to appropriate Redis queues based on required VRAM. Dynamically provisions or terminates GPU workers based on queue depth and idle time to optimize costs.
3. **Workflow Engine (DAGs)**: Supports chained processing graphs (e.g., Upload -> Separation -> Conversion -> Mastering -> ZIP). Replaces hardcoded sequences with a flexible Directed Acyclic Graph.
4. **Audio Cache**: Before enqueuing a heavy task (e.g., Demucs stem separation), the system checks the `AudioCache` for the audio hash and parameters. If found, it skips the worker and returns the cached result.

## Pluggable AI Providers
Models are not hard-wired to a single execution environment. The architecture uses a Provider Interface:
- **Local PyTorch**: Runs on self-hosted GPU workers.
- **RunPod Serverless**: Dispatches inference to scalable RunPod endpoints.
- **Hugging Face API**: Leverages managed endpoints.
- **Custom Docker**: Allows future proprietary or third-party containers.

## Plugin Architecture (Common Interfaces)
To allow modular model swapping, we define abstract base classes in `ai/models/`:

```python
class VoiceConverterInterface(ABC):
    @abstractmethod
    def convert(self, audio_path: str, model_path: str) -> str:
        pass
```

Each specific model (e.g., `RVC`, `SeedVC`) implements this interface.
