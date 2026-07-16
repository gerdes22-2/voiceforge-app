# Voice Training Pipeline

The Voice Training pipeline transforms raw audio uploads into a high-fidelity, production-ready AI Voice Model capable of professional Voice Conversion. It leverages the underlying `WorkflowEngine` and `AIProvider` runtime, rather than existing as a separate silo.

## Pipeline Architecture (DAG)

1. **Dataset Quality Analyzer**
   - Assesses the dataset items holistically (e.g., Singing coverage vs. Speech coverage). Generates a "Health Score" to preemptively warn users if training is likely to fail or yield poor results.
   
2. **Audio Cleaning Provider**
   - Implements automated DSP tasks: background noise reduction, de-clipping, loudness normalization, silence trimming, and sample rate standardization (e.g., forcing 44.1kHz).

3. **Smart Segmentation Provider**
   - Splits audio dynamically based on pauses, breaths, phrases, and chorus sections rather than arbitrary 5-second intervals. Generates contextual metadata (`pitch_range`, `energy`, `emotion`).

4. **Speaker Verification Provider**
   - Calculates speaker embeddings across all dataset items to detect anomalous voices (e.g., producer instructions, backing vocalists) to ensure the dataset is perfectly homogenous.

5. **Feature Extraction Provider**
   - Extracts model-specific training inputs like Pitch (F0) curves, Mel Spectrograms, and HuBERT/Content embeddings.

6. **Voice Training Provider (RVC)**
   - Exposes the abstract `VoiceTrainingProvider` contract. Handles iterative model training on GPUs, writing intermediate checkpoints, and logging epoch metrics and loss functions.

7. **Voice Model Evaluation Provider**
   - Automatically runs a suite of tests on the exported `.pth` model to grade its `similarity`, `naturalness`, and `singing_ability`. 

## Approval Gate
Training completion does not immediately promote a model to production. Users must manually review the Evaluation Score and invoke the Approval Gate (`POST /api/v1/voice-models/{id}/status`) to mark the model as `approved` before the `VoiceModelServer` allows it to be loaded into VRAM for inference.
