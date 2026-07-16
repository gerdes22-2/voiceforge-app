# VoiceForge Roadmap

## Completed

- **Architecture**: Fast API, Postgres, SQLAlchemy, Alembic, Docker.
- **Infrastructure**: Validate scripts, Python module setup, static analysis (mypy, ruff, pytest).
- **Database**: Core data models (User, Project, VoiceModel, Job, System, Log).
- **IAM**: JWT Authentication, Role-based Access Control (Admin, Artist, Producer, Guest).
- **Storage**: Abstract storage provider layer (Local/S3) and `FileAsset` lifecycle.
- **Workflow Engine**: DAG implementation, state management (Pending, Queued, Running, Completed), retry & cancellation.
- **AI Runtime**: `AIProvider` base contract, GPU memory manager, sandbox isolation, caching, scheduling.
- **Audio Processing**: Whisper transcription, Intelligent Stem Separation (MelBand-Roformer & HTDemucs), Quality Scoring.
- **Audio Intelligence**: BPM, key, genre, vocal mechanics analysis provider.
- **Voice Training**: Dataset analyzer, smart segmentation, speaker verification, feature extraction, RVC training loop, model evaluation.
- **Voice Conversion Pipeline**: End-to-end song replacement workflow.
  - Stem Separation
  - RVC Inference (Voice Replacement)
  - Vocal Enhancement (Noise Reduction, EQ, Compression)
  - Mixing (Instrumental + AI Vocal)
  - Export (WAV, MP3, FLAC)

## Next Steps

- Final Music Pipeline
- AI Harmonies & Adlibs
- UI/Frontend implementation
