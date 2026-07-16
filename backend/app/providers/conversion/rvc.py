import asyncio
from typing import Dict, Any
import os
import uuid
from app.providers.conversion.base import VoiceConversionProvider
from app.runtime.profile import ResourceProfile
from app.runtime.serving import VoiceModelServer

class RVCInferenceProvider(VoiceConversionProvider):
    """
    RVC (Retrieval-based Voice Conversion) inference provider.
    """
    def __init__(self):
        self._progress = 0.0
        self._is_cancelled = False
        self._temp_files = []
        
    @property
    def name(self) -> str:
        return "rvc_inference"
        
    @property
    def profile(self) -> ResourceProfile:
        return ResourceProfile(
            gpu_required=True,
            min_vram_mb=4000,
            min_ram_mb=8192,
            expected_runtime_sec=60,
            supports_cache=True,
            supports_resume=False,
            supports_cancellation=True
        )

    async def initialize(self) -> None:
        self._progress = 0.0
        self._is_cancelled = False

    async def validate(self, input_params: Dict[str, Any]) -> bool:
        required_keys = ["audio_path", "voice_model_id"]
        for k in required_keys:
            if k not in input_params:
                raise ValueError(f"Missing required parameter: {k}")
        return True

    async def prepare(self, input_params: Dict[str, Any]) -> Any:
        import shutil
        audio_path = input_params["audio_path"]
        prepared_path = f"/tmp/{uuid.uuid4()}_convert_input.wav"
        try:
            shutil.copy2(audio_path, prepared_path)
            self._temp_files.append(prepared_path)
        except Exception:
            pass
            
        return {
            "prepared_audio_path": prepared_path,
            "voice_model_id": input_params["voice_model_id"],
            "pitch_shift": input_params.get("pitch_shift", 0),
            "index_rate": input_params.get("index_rate", 0.5),
            "protect": input_params.get("protect", 0.33),
            "filter_radius": input_params.get("filter_radius", 3)
        }

    async def extract_features(self, prepared_data: Any) -> Any:
        self._progress = 0.2
        await asyncio.sleep(0.05) # simulate f0 / hubert extraction
        return prepared_data

    async def convert(self, features_data: Any) -> Any:
        model_id = features_data["voice_model_id"]
        # Load the model from serving layer
        model = await VoiceModelServer.load_model(model_id, vram_required_mb=2000)
        
        self._progress = 0.5
        
        for i in range(1, 10):
            if self._is_cancelled:
                raise InterruptedError("Conversion cancelled")
            await asyncio.sleep(0.05)
            self._progress = 0.5 + (i * 0.05)
            
        output_path = f"/tmp/converted_{uuid.uuid4()}.wav"
        with open(output_path, "wb") as f:
            f.write(b"converted_audio_data")
            
        self._temp_files.append(output_path)
        
        return {
            "converted_audio_path": output_path,
            "quality_score": 93.5 # simulated mock score
        }

    async def run(self, prepared_data: Any) -> Any:
        features = await self.extract_features(prepared_data)
        return await self.convert(features)

    async def monitor(self) -> float:
        return self._progress

    async def cancel(self) -> None:
        self._is_cancelled = True

    async def cleanup(self) -> None:
        for path in self._temp_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
        self._temp_files.clear()

    async def publish_artifacts(self, run_result: Any) -> Dict[str, str]:
        return {
            "converted_audio_url": f"local://storage/{os.path.basename(run_result['converted_audio_path'])}",
            "quality_score": run_result["quality_score"]
        }
