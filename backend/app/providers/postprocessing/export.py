import asyncio
from typing import Dict, Any
import os
import uuid
from app.runtime.base import AIProvider
from app.runtime.profile import ResourceProfile

class ExportProvider(AIProvider):
    """
    Exports the final mixed track to WAV, MP3, or FLAC.
    """
    def __init__(self):
        self._progress = 0.0
        self._is_cancelled = False
        self._temp_files = []
        
    @property
    def name(self) -> str:
        return "export"
        
    @property
    def profile(self) -> ResourceProfile:
        return ResourceProfile(
            gpu_required=False,
            min_vram_mb=0,
            min_ram_mb=1024,
            expected_runtime_sec=15,
            supports_cache=True,
            supports_resume=False,
            supports_cancellation=True
        )

    async def initialize(self) -> None:
        self._progress = 0.0
        self._is_cancelled = False

    async def validate(self, input_params: Dict[str, Any]) -> bool:
        if "audio_path" not in input_params:
            raise ValueError("audio_path missing")
        return True

    async def prepare(self, input_params: Dict[str, Any]) -> Any:
        return input_params

    async def run(self, prepared_data: Any) -> Any:
        if self._is_cancelled:
            raise InterruptedError("Export cancelled")
            
        format_ext = prepared_data.get("format", "mp3")
        
        self._progress = 0.5
        await asyncio.sleep(0.05)
        
        output_path = f"/tmp/export_{uuid.uuid4()}.{format_ext}"
        with open(output_path, "wb") as f:
            f.write(b"exported_audio_data")
        self._temp_files.append(output_path)
        
        self._progress = 1.0
        return {"exported_audio_path": output_path, "format": format_ext}

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
        return {"exported_audio_url": f"local://storage/{os.path.basename(run_result['exported_audio_path'])}"}
