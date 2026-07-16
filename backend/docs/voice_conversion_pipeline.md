# Voice Conversion Pipeline

This pipeline is the core product feature of VoiceForge, transforming an original song's vocals into the user's trained AI voice while preserving the underlying music and original vocal characteristics.

## Pipeline Architecture (DAG)

1. **Stem Separation**
   - Extracts the original vocal track and instrumental background using robust separation providers like MelBand-Roformer or HTDemucs.

2. **RVC Inference Provider (Voice Conversion)**
   - The original separated vocal stem and the user's specified Voice Model ID are passed to `RVCInferenceProvider`.
   - The provider relies on the `VoiceModelServer` (and `GPUMemoryManager`) to dynamically load weights into VRAM.
   - It performs feature extraction and inference. Key parameters include:
     - `pitch_shift`: Adjusting the target pitch for gender differences or specific octaves.
     - `index_rate`: Feature retrieval strength to maintain target voice fidelity.
     - `protect`: Consonant preservation.
     - `filter_radius`: Smoothing artifacts.
   - It outputs the raw converted vocal stem.

3. **Vocal Enhancement Provider**
   - Acts as an automated mixing engineer for the raw AI output. 
   - Runs DSP operations in sequence: Noise Reduction -> EQ -> Compression -> De-essing -> Limiter.
   - Outputs a polished, studio-quality vocal stem.

4. **Mixing Provider**
   - Recombines the enhanced AI vocal stem with the original instrumental stem.
   - Adjusts vocal volume and applies spatial effects (Reverb, Delay, Stereo width).

5. **Export Provider**
   - Transcodes the final mixdown into the requested formats (WAV, MP3, FLAC) and registers it as an `ExportArtifact`.

## Execution Mechanics

- Each step implements the standard `AIProvider` contract (`initialize()`, `validate()`, `prepare()`, `run()`, `cleanup()`).
- The `WorkflowEngine` manages task dependencies ensuring conversion doesn't start until stem separation finishes.
- Tasks declare resource profiles (`ResourceProfile`) for intelligent GPU scheduling, track progress, support caching, and provide graceful cancellation.
