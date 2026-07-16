import pytest
import asyncio
import os
from app.runtime.registry import ProviderRegistry
from app.providers.transcription.whisper import WhisperProvider

@pytest.fixture(autouse=True)
def setup_providers():
    ProviderRegistry.register(WhisperProvider)

def test_registry_contains_whisper():
    provider = ProviderRegistry.get_provider("whisper_v3")
    assert isinstance(provider, WhisperProvider)
    assert provider.name == "whisper_v3"
    assert provider.profile.gpu_required is True

@pytest.mark.asyncio
async def test_whisper_lifecycle(tmp_path):
    provider = ProviderRegistry.get_provider("whisper_v3")
    
    # Create a dummy audio file for validation
    dummy_audio = tmp_path / "dummy.wav"
    dummy_audio.write_bytes(b"RIFF")
    
    input_params = {"audio_path": str(dummy_audio)}
    
    await provider.initialize()
    
    is_valid = await provider.validate(input_params)
    assert is_valid is True
    
    prep_data = await provider.prepare(input_params)
    assert "prepared_audio_path" in prep_data
    
    run_result = await provider.run(prep_data)
    assert "transcript_path" in run_result
    assert run_result["text"] == "This is a mocked transcription from the Whisper model."
    
    progress = await provider.monitor()
    assert progress == 1.0
    
    artifacts = await provider.publish_artifacts(run_result)
    assert "transcript_url" in artifacts
    
    await provider.cleanup()

@pytest.mark.asyncio
async def test_whisper_cancellation(tmp_path):
    provider = ProviderRegistry.get_provider("whisper_v3")
    
    dummy_audio = tmp_path / "dummy_cancel.wav"
    dummy_audio.write_bytes(b"RIFF")
    input_params = {"audio_path": str(dummy_audio)}
    
    await provider.initialize()
    prep_data = await provider.prepare(input_params)
    
    # Run in background
    task = asyncio.create_task(provider.run(prep_data))
    
    # Give it a moment to start, then cancel
    await asyncio.sleep(0.05)
    await provider.cancel()
    
    with pytest.raises(InterruptedError):
        await task
        
    await provider.cleanup()
