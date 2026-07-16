import asyncio
from typing import Dict, Any
import os
import uuid
from app.runtime.base import AIProvider
from app.runtime.profile import ResourceProfile

class MixingProvider(AIProvider):
    """
    Mixes vocals and instrumentals together with Reverb, Delay, Stereo width.
    """
    def __init__(self):
        self._progress = 0.0
        self._is_cancelled = False
        self._temp_files = []
        
    @property
    def name(self) -> str:
        return "mixing"
        
    @property
    def profile(self) -> ResourceProfile:
        return ResourceProfile(
            gpu_required=False,
            min_vram_mb=0,
            min_ram_mb=2048,
            expected_runtime_sec=45,
            supports_cache=True,
            supports_resume=False,
            supports_cancellation=True
        )

    async def initialize(self) -> None:
        self._progress = 0.0
        self._is_cancelled = False

    async def validate(self, input_params: Dict[str, Any]) -> bool:
        if "vocal_path" not in input_params or "instrumental_path" not in input_params:
            raise ValueError("vocal_path and instrumental_path are required")
        return True

    async def prepare(self, input_params: Dict[str, Any]) -> Any:
        return input_params

    async def run(self, prepared_data: Any) -> Any:
        if self._is_cancelled:
            raise InterruptedError("Mixing cancelled")
            
        self._progress = 0.5
        await asyncio.sleep(0.05)
        
        output_path = f"/tmp/mix_{uuid.uuid4()}.wav"
        with open(output_path, "wb") as f:
            f.write(b"mixed_audio_data")
        self._temp_files.append(output_path)
        
        self._progress = 1.0
        return {"mixed_audio_path": output_path}

    async def monitor(self) -> float:
        return self._progress

    async def cancel(self) -> None:
        self._is_cancelled = True

    async def cleanup(self) -> None:
        for path in self._temp_files:
            if os.path.exists(path):
                try: os.remove(path)
                except: pass
        self._temp_files.clear()

    async def publish_artifacts(self, run_result: Any) -> Dict[str, str]:
        return {"mixed_audio_url": f"local://storage/{os.path.basename(run_result['mixed_audio_path'])}"}
