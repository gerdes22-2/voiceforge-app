# Audio Intelligence & Voice Model Serving

## Advanced Audio Intelligence
Before progressing to Voice Training, the platform integrates an `AudioIntelligenceProvider` that extracts rich, structured metadata from uploaded audio. This provider acts as an expert musicologist and vocal coach, analyzing:
- **Song Structure & Musicality**: BPM, key, genre probability, energy, and section bounding boxes (Intro, Verse, Chorus, etc.)
- **Vocal Mechanics**: Pitch range (e.g. G2 - C5), vibrato depth, breathiness, brightness, and rhythm accuracy.

These insights are crucial downstream. They allow the Voice Conversion engine to preserve the exact stylistic timing, dynamics, and expressive character of the original singer when applying a new voice.

## Voice Model Evaluation System
A dedicated `VoiceModelEvaluationProvider` runs automatically after a Voice Training job completes. It ensures models are not just "exported", but objectively validated across axes such as:
- Similarity to the target artist
- Naturalness of the synthesis
- Stability over time
- Pitch accuracy and singing ability

## Voice Model Serving Layer
To prevent workers from redundantly loading models and exhausting VRAM, the `VoiceModelServer` handles localized model caching, integrated directly with a `GPUMemoryManager`. 

**Execution Flow**:
1. Workflow Engine schedules a Conversion task on a worker.
2. Worker queries `VoiceModelServer.load_model(model_id)`.
3. If the model is not in VRAM, the Server checks `GPUMemoryManager.allocate()`.
4. If VRAM is available, the model weights are loaded and locked.
5. Future tasks requesting the same `model_id` instantly receive the cached tensor weights without incurring a disk/network load penalty or double-allocating VRAM.
