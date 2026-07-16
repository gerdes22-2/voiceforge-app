import os

with open("backend/tests/integration/test_conversion.py", "w") as f:
    f.write("""import pytest
import asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.storage import FileAsset
from app.models.workflow import Workflow, WorkflowTask, TaskState
from app.orchestration.engine import WorkflowEngine
from app.orchestration.builder import WorkflowBuilder
from app.providers.conversion.rvc import RVCInferenceProvider
from app.providers.postprocessing.enhancement import VocalEnhancementProvider
from app.providers.postprocessing.mixing import MixingProvider
from app.providers.postprocessing.export import ExportProvider
from app.db.session import async_session_maker

@pytest.mark.asyncio
async def test_conversion_providers_lifecycle(tmp_path):
    # Setup dummy paths
    dummy_vocal = tmp_path / "dummy_vocal.wav"
    dummy_vocal.write_bytes(b"RIFF vocal")
    dummy_instrumental = tmp_path / "dummy_inst.wav"
    dummy_instrumental.write_bytes(b"RIFF inst")
    
    # RVC
    rvc = RVCInferenceProvider()
    await rvc.initialize()
    params = {
        "audio_path": str(dummy_vocal),
        "voice_model_id": str(uuid4()),
        "pitch_shift": 0
    }
    assert await rvc.validate(params)
    prep = await rvc.prepare(params)
    res = await rvc.run(prep)
    arts = await rvc.publish_artifacts(res)
    assert "converted_audio_url" in arts
    
    # Enhancement
    enh = VocalEnhancementProvider()
    await enh.initialize()
    ep = {"audio_path": res["converted_audio_path"]}
    assert await enh.validate(ep)
    eprep = await enh.prepare(ep)
    eres = await enh.run(eprep)
    earts = await enh.publish_artifacts(eres)
    assert "enhanced_audio_url" in earts
    
    # Mix
    mix = MixingProvider()
    await mix.initialize()
    mp = {"vocal_path": eres["enhanced_audio_path"], "instrumental_path": str(dummy_instrumental)}
    assert await mix.validate(mp)
    mprep = await mix.prepare(mp)
    mres = await mix.run(mprep)
    marts = await mix.publish_artifacts(mres)
    assert "mixed_audio_url" in marts
    
    # Export
    exp = ExportProvider()
    await exp.initialize()
    expp = {"audio_path": mres["mixed_audio_path"], "format": "mp3"}
    assert await exp.validate(expp)
    exprep = await exp.prepare(expp)
    expres = await exp.run(exprep)
    exparts = await exp.publish_artifacts(expres)
    assert "exported_audio_url" in exparts
    
    # Cleanup
    await rvc.cleanup()
    await enh.cleanup()
    await mix.cleanup()
    await exp.cleanup()
""")
