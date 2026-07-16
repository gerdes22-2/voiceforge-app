from .celery_app import celery_app
import time
import logging
import asyncio
import os
from worker.ai.services.stem_separation_service import stem_service
from worker.ai.providers.separation.demucs_provider import DemucsProvider
from worker.ai.providers.separation.melband_provider import MelBandRoformerProvider
from worker.ai.providers.quality.librosa_analyzer import LibrosaQualityAnalyzer
from shared.ai.models import SeparationResult

logger = logging.getLogger("worker.audio_tasks")

# Initialize and register providers
analyzer = LibrosaQualityAnalyzer()
stem_service._quality_analyzer = analyzer
stem_service.register_provider(DemucsProvider())
stem_service.register_provider(MelBandRoformerProvider())

@celery_app.task(bind=True, name="stem_separation")
def separate_stems_task(self, song_id: str, file_uuid: str):
    logger.info(f"Starting stem separation for song {song_id}")
    
    # In a real environment, we would:
    # 1. Download the file from storage using file_uuid
    # 2. Save it to a local temporary path
    input_audio_path = f"/tmp/{file_uuid}.wav"
    output_dir = f"/tmp/out_{song_id}"
    
    # Create mock input file so our simulated providers don't complain
    os.makedirs(os.path.dirname(input_audio_path), exist_ok=True)
    with open(input_audio_path, "wb") as f:
        f.write(b"MOCK_INPUT")
        
    async def progress_callback(progress: float, message: str):
        self.update_state(state="PROGRESS", meta={"progress": progress, "song_id": song_id, "message": message})
        logger.info(f"Progress {progress}%: {message}")
        
    async def run_separation():
        # User requested Demucs as first provider, but we built it for future models too.
        # MelBand Roformer is a great modern alternative to test the fallback/scoring.
        preferred_providers = ["demucs", "melband_roformer"]
        
        result: SeparationResult = await stem_service.separate(
            audio_file_path=input_audio_path,
            output_dir=output_dir,
            preferred_providers=preferred_providers,
            progress_callback=progress_callback,
            min_acceptable_score=0.80
        )
        return result
        
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    result = loop.run_until_complete(run_separation())
    
    # In a real environment, we would:
    # 3. Upload the resulting stems back to storage
    # 4. Cleanup local temporary files
    
    output_meta = {
        "status": "completed",
        "song_id": song_id,
        "stems": list(result.stems.keys()),
        "provider_used": result.provider_used,
        "metadata": result.metadata
    }
    
    if result.quality:
        output_meta["quality_score"] = result.quality.model_dump()
        
    logger.info(f"Stem separation completed for song {song_id} using {result.provider_used}")
    return output_meta
