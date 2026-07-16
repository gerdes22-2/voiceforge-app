import os

with open("backend/tests/integration/test_end_to_end.py", "w") as f:
    f.write("""import pytest
import asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.storage import FileAsset
from app.models.workflow import Workflow, WorkflowTask, TaskState
from app.orchestration.engine import WorkflowEngine
from app.orchestration.scoring import ProviderScoringSystem, QualityComparator
from app.providers.separation.melband import MelBandRoformerProvider
from app.providers.separation.demucs import DemucsProvider
from app.db.session import async_session_maker

@pytest.mark.asyncio
async def test_end_to_end_stem_separation_pipeline():
    \"\"\"
    Simulates the end-to-end flow:
    Upload -> Workflow DAG -> Provider Scheduling -> MelBand/Demucs -> Quality Comparison
    \"\"\"
    async with async_session_maker() as db:
        # 1. Setup Mock User, Project, and Uploaded File
        user_id = uuid4()
        project = Project(name="E2E Test Project", user_id=user_id)
        db.add(project)
        await db.commit()
        await db.refresh(project)
        
        file_asset = FileAsset(
            user_id=user_id,
            file_name="test_song.wav",
            storage_provider="local",
            storage_path="/tmp/test_song.wav",
            mime_type="audio/wav",
            size_bytes=1024,
            is_validated=True
        )
        db.add(file_asset)
        await db.commit()
        await db.refresh(file_asset)
        
        # We need a dummy file on disk for the providers to "copy"
        with open("/tmp/test_song.wav", "wb") as dummy_f:
            dummy_f.write(b"RIFF dummy audio")
            
        # 2. Build DAG Workflow
        workflow = Workflow(
            project_id=project.id,
            name="Intelligent Stem Separation",
            status=TaskState.PENDING,
            target_asset_id=file_asset.id
        )
        db.add(workflow)
        await db.flush()
        
        # Parallel Tasks: MelBand & Demucs
        melband_task = WorkflowTask(
            workflow_id=workflow.id,
            task_type="stem_separation",
            depends_on=[],
            input_params={"audio_path": file_asset.storage_path, "provider": "melband_roformer"}
        )
        demucs_task = WorkflowTask(
            workflow_id=workflow.id,
            task_type="stem_separation",
            depends_on=[],
            input_params={"audio_path": file_asset.storage_path, "provider": "htdemucs"}
        )
        db.add_all([melband_task, demucs_task])
        await db.flush()
        
        # Evaluation Task
        eval_task = WorkflowTask(
            workflow_id=workflow.id,
            task_type="quality_evaluation",
            depends_on=[str(melband_task.id), str(demucs_task.id)],
            input_params={"target": "stem_separation"}
        )
        db.add(eval_task)
        await db.commit()
        
        # 3. Simulate Workflow Engine + Scheduler
        runnable = await WorkflowEngine.get_runnable_tasks(db, workflow.id)
        assert len(runnable) == 2 # Both separation tasks are ready
        
        # 4. Execute Providers (Mocking the Worker)
        melband = MelBandRoformerProvider()
        demucs = DemucsProvider()
        
        await melband.initialize()
        assert await melband.validate(melband_task.input_params)
        prep_m = await melband.prepare(melband_task.input_params)
        res_m = await melband.run(prep_m)
        arts_m = await melband.publish_artifacts(res_m)
        
        melband_task.status = TaskState.COMPLETED
        melband_task.output_artifacts = arts_m
        
        await demucs.initialize()
        assert await demucs.validate(demucs_task.input_params)
        prep_d = await demucs.prepare(demucs_task.input_params)
        res_d = await demucs.run(prep_d)
        arts_d = await demucs.publish_artifacts(res_d)
        
        demucs_task.status = TaskState.COMPLETED
        demucs_task.output_artifacts = arts_d
        
        await db.commit()
        
        # 5. Engine re-evaluates -> Eval Task is now runnable
        runnable = await WorkflowEngine.get_runnable_tasks(db, workflow.id)
        assert len(runnable) == 1
        assert runnable[0].id == eval_task.id
        
        # 6. Quality Comparison Logic
        eval_results = [arts_m, arts_d]
        best = QualityComparator.evaluate_best_stem(eval_results)
        
        # MelBand has 95.0, Demucs has 91.0
        assert best == arts_m
        assert best["quality_score"] == 95.0
        
        eval_task.status = TaskState.COMPLETED
        eval_task.output_artifacts = {"best_stems": best}
        workflow.status = TaskState.COMPLETED
        
        await db.commit()
        
        # Cleanup temp files
        await melband.cleanup()
        await demucs.cleanup()
""")
