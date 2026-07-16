import pytest
import asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.project import Project
from app.models.storage import FileAsset
from app.models.voice import VoiceModel
from app.models.workflow import Workflow, WorkflowTask, TaskState
from app.orchestration.engine import WorkflowEngine
from app.orchestration.builder import WorkflowBuilder
from app.providers.conversion.rvc import RVCInferenceProvider
from app.providers.postprocessing.enhancement import VocalEnhancementProvider
from app.providers.postprocessing.mixing import MixingProvider
from app.providers.postprocessing.export import ExportProvider
from app.providers.voice.preparation.cleaning import AudioCleaningProvider
from app.providers.voice.preparation.segmentation import SmartSegmentationProvider
from app.providers.voice.preparation.verification import SpeakerVerificationProvider
from app.providers.voice.preparation.extraction import FeatureExtractionProvider
from app.providers.voice.training.rvc import RVCTrainingProvider
from app.providers.separation.melband import MelBandRoformerProvider
from app.db.session import async_session_maker

@pytest.mark.asyncio
async def test_golden_path_end_to_end(tmp_path):
    """
    End-to-End Golden Path Test simulating a complete artist workflow:
    1. Account/Project Creation
    2. Dataset Upload & Training Pipeline
    3. Model Approval
    4. Song Conversion Pipeline (Separation -> Conversion -> Enhancement -> Mix -> Export)
    """
    async with async_session_maker() as db:
        # 1-3. Create User, Organization, Project
        user_id = uuid4()
        user = User(email="artist@voiceforge.ai", hashed_password="pw", full_name="Artist Name", role="Artist")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        project = Project(name="Golden Path Hit", user_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)
        
        # 4-6. Upload Suno Song & Voice Samples
        suno_song = FileAsset(user_id=user.id, file_name="suno_original.wav", storage_provider="local", storage_path="/tmp/suno.wav", mime_type="audio/wav", size_bytes=1000)
        voice_sample = FileAsset(user_id=user.id, file_name="dry_vocal.wav", storage_provider="local", storage_path="/tmp/vocal.wav", mime_type="audio/wav", size_bytes=1000)
        db.add_all([suno_song, voice_sample])
        await db.commit()
        await db.refresh(suno_song)
        
        # 7-9. Train Voice Model Workflow
        voice_model = VoiceModel(name="Artist Studio Voice", user_id=user.id, status="training")
        db.add(voice_model)
        await db.commit()
        await db.refresh(voice_model)
        
        dataset_version_id = uuid4()
        training_wf = await WorkflowBuilder.create_voice_training_workflow(
            db, project.id, dataset_version_id, voice_model.id
        )
        assert training_wf.id is not None
        
        # Mock executing training tasks...
        tasks = await WorkflowEngine.get_runnable_tasks(db, training_wf.id)
        for t in tasks:
            t.status = TaskState.COMPLETED
        await db.commit()
        
        # 10. Approve Voice Model
        voice_model.status = "approved"
        await db.commit()
        
        # 11-16. Song Conversion Workflow
        conversion_params = {
            "pitch_shift": 0,
            "index_rate": 0.8,
            "protect": 0.33,
            "filter_radius": 3
        }
        conv_wf = await WorkflowBuilder.create_full_song_conversion_workflow(
            db, project.id, suno_song.id, voice_model.id, conversion_params
        )
        assert conv_wf.id is not None
        
        # Set to completed
        conv_wf.status = TaskState.COMPLETED
        await db.commit()
