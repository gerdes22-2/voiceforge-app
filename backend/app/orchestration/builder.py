from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflow import Workflow, WorkflowTask, TaskState

class WorkflowBuilder:
    """
    Constructs the DAG dynamically.
    """
    @staticmethod
    async def create_vocal_processing_workflow(db: AsyncSession, project_id: UUID, target_asset_id: UUID) -> Workflow:
        """
        Upload -> Metadata -> Stem Separation -> (Transcribe & Pitch) -> Conversion -> Master
        """
        workflow = Workflow(
            project_id=project_id,
            name="Full Vocal Processing",
            status=TaskState.PENDING,
            target_asset_id=target_asset_id
        )
        db.add(workflow)
        await db.flush() # get ID
        
        # Node 1: Metadata
        metadata = WorkflowTask(
            workflow_id=workflow.id,
            task_type="metadata_extraction",
            depends_on=[],
            input_params={"asset_id": str(target_asset_id)}
        )
        db.add(metadata)
        await db.flush()
        
        # Node 2: Stem Separation
        stem_sep = WorkflowTask(
            workflow_id=workflow.id,
            task_type="stem_separation",
            depends_on=[str(metadata.id)],
            input_params={"model": "htdemucs"}
        )
        db.add(stem_sep)
        await db.flush()
        
        # Node 3a: Transcribe
        transcribe = WorkflowTask(
            workflow_id=workflow.id,
            task_type="transcription",
            depends_on=[str(stem_sep.id)],
            input_params={"model": "whisper-v3"}
        )
        db.add(transcribe)
        
        # Node 3b: Pitch Detection
        pitch = WorkflowTask(
            workflow_id=workflow.id,
            task_type="pitch_detection",
            depends_on=[str(stem_sep.id)],
            input_params={"algorithm": "rmvpe"}
        )
        db.add(pitch)
        await db.flush()
        
        # Node 4: Voice Conversion
        conversion = WorkflowTask(
            workflow_id=workflow.id,
            task_type="voice_conversion",
            depends_on=[str(transcribe.id), str(pitch.id)],
            input_params={"f0_method": "rmvpe"}
        )
        db.add(conversion)
        await db.flush()
        
        await db.commit()
        return workflow

    @staticmethod
    async def create_voice_training_workflow(
        db: AsyncSession, 
        project_id: UUID, 
        dataset_version_id: UUID, 
        voice_model_id: UUID
    ) -> Workflow:
        """
        Quality -> Clean -> Segment -> Verify -> Extract -> Train -> Evaluate
        """
        workflow = Workflow(
            project_id=project_id,
            name="Voice Model Training Pipeline",
            status=TaskState.PENDING,
            target_asset_id=None
        )
        db.add(workflow)
        await db.flush()

        quality = WorkflowTask(
            workflow_id=workflow.id,
            task_type="dataset_quality_analyzer",
            depends_on=[],
            input_params={"dataset_version_id": str(dataset_version_id), "dataset_items": []}
        )
        db.add(quality)
        await db.flush()

        cleaning = WorkflowTask(
            workflow_id=workflow.id,
            task_type="audio_cleaning",
            depends_on=[str(quality.id)],
            input_params={"dataset_version_id": str(dataset_version_id)}
        )
        db.add(cleaning)
        await db.flush()

        segmentation = WorkflowTask(
            workflow_id=workflow.id,
            task_type="smart_segmentation",
            depends_on=[str(cleaning.id)],
            input_params={}
        )
        db.add(segmentation)
        await db.flush()

        verification = WorkflowTask(
            workflow_id=workflow.id,
            task_type="speaker_verification",
            depends_on=[str(segmentation.id)],
            input_params={}
        )
        db.add(verification)
        await db.flush()

        extraction = WorkflowTask(
            workflow_id=workflow.id,
            task_type="feature_extraction",
            depends_on=[str(verification.id)],
            input_params={}
        )
        db.add(extraction)
        await db.flush()

        training = WorkflowTask(
            workflow_id=workflow.id,
            task_type="rvc_trainer",
            depends_on=[str(extraction.id)],
            input_params={"voice_model_id": str(voice_model_id), "epochs": 100}
        )
        db.add(training)
        await db.flush()

        evaluation = WorkflowTask(
            workflow_id=workflow.id,
            task_type="voice_model_evaluator",
            depends_on=[str(training.id)],
            input_params={"model_id": str(voice_model_id)}
        )
        db.add(evaluation)
        
        await db.commit()
        return workflow

    @staticmethod
    async def create_full_song_conversion_workflow(
        db: AsyncSession, 
        project_id: UUID, 
        target_asset_id: UUID, 
        voice_model_id: UUID,
        conversion_params: dict
    ) -> Workflow:
        """
        End-to-End pipeline:
        Upload -> Stem Separation -> Voice Conversion -> Vocal Enhancement -> Mixing -> Export
        """
        workflow = Workflow(
            project_id=project_id,
            name="Full Song Voice Conversion Pipeline",
            status=TaskState.PENDING,
            target_asset_id=target_asset_id
        )
        db.add(workflow)
        await db.flush()

        # 1. Stem Separation (MelBand)
        separation = WorkflowTask(
            workflow_id=workflow.id,
            task_type="stem_separation",
            depends_on=[],
            input_params={"provider": "melband_roformer"} # Assume input_params filled correctly by engine
        )
        db.add(separation)
        await db.flush()

        # 2. Voice Conversion
        conversion_params["voice_model_id"] = str(voice_model_id)
        conversion = WorkflowTask(
            workflow_id=workflow.id,
            task_type="rvc_inference",
            depends_on=[str(separation.id)],
            input_params=conversion_params
        )
        db.add(conversion)
        await db.flush()

        # 3. Vocal Enhancement
        enhancement = WorkflowTask(
            workflow_id=workflow.id,
            task_type="vocal_enhancement",
            depends_on=[str(conversion.id)],
            input_params={}
        )
        db.add(enhancement)
        await db.flush()

        # 4. Mixing
        mixing = WorkflowTask(
            workflow_id=workflow.id,
            task_type="mixing",
            depends_on=[str(separation.id), str(enhancement.id)],
            input_params={}
        )
        db.add(mixing)
        await db.flush()
        
        # 5. Export
        export = WorkflowTask(
            workflow_id=workflow.id,
            task_type="export",
            depends_on=[str(mixing.id)],
            input_params={"format": "mp3"}
        )
        db.add(export)
        
        await db.commit()
        return workflow
