# End-to-End Stem Separation Workflow

The Stem Separation pipeline validates the entire AI Orchestration and Runtime layers, proving that all the sub-systems work in harmony. 

## Providers Integration
Two specialized audio source separation models are integrated adhering strictly to the `AIProvider` contract:
- **MelBand-Roformer**: Serves as the high-quality default provider, requiring an estimated 8GB of VRAM and capable of generating extremely crisp stems.
- **HTDemucs**: Serves as the robust fallback provider (or parallel execution target for comparisons), ensuring high availability. 

## Quality-Based Decision Logic
The workflow employs an automatic `QualityComparator` and `ProviderScoringSystem`. Instead of forcing manual model selection, the pipeline can execute both providers (or fallback in case of failure), evaluate the resulting `quality_score`, and intelligently select the optimal stems (e.g. MelBand Score 95 vs Demucs Score 91 -> keep MelBand). 

## End-to-End Workflow Validation
A complete workflow DAG has been defined and tested:
1. **Target Asset Check**: Ensures the uploaded `FileAsset` is valid.
2. **Parallel Scheduling**: Invokes both `MelBandRoformerProvider` and `DemucsProvider`.
3. **Artifact Generation**: Outputs `.wav` files mapping to new `FileAsset` URLs.
4. **Quality Evaluation**: A deterministic task assesses both outputs and retains the higher-rated artifacts.
5. **Caching & Cleanup**: Stems are properly routed to the `ArtifactManager` and all transient model resources are wiped from VRAM and disk. 
