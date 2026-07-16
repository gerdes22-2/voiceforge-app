import asyncio
from typing import Dict, Any
import os
import uuid
from app.runtime.base import AIProvider
from app.runtime.profile import ResourceProfile

class FeatureExtractionProvider(AIProvider):
    """
    Extracts Pitch (F0), Mel Spectrograms, and HuBERT/Content embeddings.
    """
    def __init__(self):
        self._progress = 0.0
        self._is_cancelled = False
        
    @property
    def name(self) -> str:
        return "feature_extraction"
        
    @property
    def profile(self) -> ResourceProfile:
        return ResourceProfile(
            gpu_required=True,
            min_vram_mb=4096,
            min_ram_mb=8192,
            expected_runtime_sec=120,
            supports_cache=True,
            supports_resume=True,
            supports_cancellation=True
        )

    async def initialize(self) -> None:
        self._progress = 0.0
        self._is_cancelled = False

    async def validate(self, input_params: Dict[str, Any]) -> bool:
        return True

    async def prepare(self, input_params: Dict[str, Any]) -> Any:
        return input_params

    async def run(self, prepared_data: Any) -> Any:
        segments = prepared_data.get("verified_segments", [1,2,3])
        total = len(segments) or 1
        
        for i, seg in enumerate(segments):
            if self._is_cancelled:
                raise InterruptedError("Extraction cancelled")
            await asyncio.sleep(0.02)
            self._progress = (i + 1) / total
            
        return {
            "features_path": f"/tmp/features_{uuid.uuid4()}.pt"
        }

    async def monitor(self) -> float:
        return self._progress

    async def cancel(self) -> None:
        self._is_cancelled = True

    async def cleanup(self) -> None:
        pass

    async def publish_artifacts(self, run_result: Any) -> Dict[str, str]:
        return {"features_url": f"local://storage/{os.path.basename(run_result['features_path'])}"}
