import os

with open("backend/app/orchestration/builder.py", "a") as f:
    f.write("""
    @staticmethod
    async def create_full_song_conversion_workflow(
        db: AsyncSession, 
        project_id: UUID, 
        target_asset_id: UUID, 
        voice_model_id: UUID,
        conversion_params: dict
    ) -> Workflow:
        \"\"\"
        End-to-End pipeline:
        Upload -> Stem Separation -> Voice Conversion -> Vocal Enhancement -> Mixing -> Export
        \"\"\"
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
""")
