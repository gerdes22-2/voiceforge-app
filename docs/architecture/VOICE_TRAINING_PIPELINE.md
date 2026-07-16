# VoiceForge AI Studio - Voice Training Pipeline

1. **Dataset Ingestion**: Upload raw audio.
2. **Preprocessing**: 
   - Silence trimming
   - Noise detection (DeepFilterNet)
   - Sample normalization
3. **Quality Scoring**: Automated analysis using `Essentia` to check for frequency range, clipping, and clarity.
4. **Training**: Enqueue training job to GPU worker.
5. **Versioning**: Save checkpoints with metadata.
