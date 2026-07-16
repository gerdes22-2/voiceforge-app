import os

with open("backend/app/providers/__init__.py", "a") as f:
    f.write("from app.providers.voice.preparation.cleaning import AudioCleaningProvider\n")
    f.write("from app.providers.voice.preparation.segmentation import SmartSegmentationProvider\n")
    f.write("from app.providers.voice.preparation.verification import SpeakerVerificationProvider\n")
    f.write("from app.providers.voice.preparation.extraction import FeatureExtractionProvider\n")
    f.write("from app.providers.voice.training.rvc import RVCTrainingProvider\n")
    f.write("ProviderRegistry.register(AudioCleaningProvider)\n")
    f.write("ProviderRegistry.register(SmartSegmentationProvider)\n")
    f.write("ProviderRegistry.register(SpeakerVerificationProvider)\n")
    f.write("ProviderRegistry.register(FeatureExtractionProvider)\n")
    f.write("ProviderRegistry.register(RVCTrainingProvider)\n")

# Update builder to include the new workflow
with open("backend/app/orchestration/builder.py", "a") as f:
    f.write("""
    @staticmethod
    async def create_voice_training_workflow(
        db: AsyncSession, 
        project_id: UUID, 
        dataset_version_id: UUID, 
        voice_model_id: UUID
    ) -> Workflow:
        \"\"\"
        Quality -> Clean -> Segment -> Verify -> Extract -> Train -> Evaluate
        \"\"\"
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
""")
