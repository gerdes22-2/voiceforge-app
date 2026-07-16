import logging
from typing import Optional, List, Dict, Callable, Awaitable
from shared.ai.interfaces import StemSeparationProvider, AudioQualityAnalyzerProvider
from shared.ai.models import SeparationResult

logger = logging.getLogger("ai.services.stem_separation")

class StemSeparationService:
    def __init__(self, quality_analyzer: Optional[AudioQualityAnalyzerProvider] = None):
        self._providers: Dict[str, StemSeparationProvider] = {}
        self._quality_analyzer = quality_analyzer
        
    def register_provider(self, provider: StemSeparationProvider):
        self._providers[provider.provider_name] = provider
        
    async def separate(
        self,
        audio_file_path: str,
        output_dir: str,
        preferred_providers: List[str],
        progress_callback: Callable[[float, str], Awaitable[None]] = None,
        min_acceptable_score: float = 0.75
    ) -> SeparationResult:
        """
        Attempts to separate audio using a prioritized list of providers.
        If a quality analyzer is configured, evaluates the output.
        If the output is below min_acceptable_score, falls back to the next provider.
        """
        
        last_error = None
        best_result = None
        
        for provider_name in preferred_providers:
            provider = self._providers.get(provider_name)
            if not provider:
                logger.warning(f"Provider {provider_name} not registered. Skipping.")
                continue
                
            try:
                logger.info(f"Attempting separation with {provider_name}")
                if progress_callback:
                    await progress_callback(0.0, f"Starting separation with {provider_name}")
                    
                result = await provider.separate(audio_file_path, output_dir, progress_callback)
                
                # Quality Analysis Gate
                if self._quality_analyzer and "vocals" in result.stems and "instrumental" in result.stems:
                    if progress_callback:
                        await progress_callback(95.0, "Analyzing separation quality")
                        
                    score = await self._quality_analyzer.analyze_stems(
                        result.stems["vocals"], 
                        result.stems["instrumental"]
                    )
                    result.quality = score
                    
                    logger.info(f"{provider_name} separation quality score: {score.confidence_score}")
                    
                    if score.confidence_score >= min_acceptable_score:
                        if progress_callback:
                            await progress_callback(100.0, "Completed successfully")
                        return result
                    else:
                        logger.warning(f"{provider_name} score {score.confidence_score} is below threshold {min_acceptable_score}.")
                        # Keep track of the best one in case all fail the threshold
                        if not best_result or (best_result.quality and score.confidence_score > best_result.quality.confidence_score):
                            best_result = result
                else:
                    # No quality analyzer, return first successful result
                    if progress_callback:
                        await progress_callback(100.0, "Completed successfully")
                    return result
                    
            except Exception as e:
                logger.error(f"Error using provider {provider_name}: {e}", exc_info=True)
                last_error = e
                
        # If we went through all and none met the threshold, return the best we got
        if best_result:
            logger.warning(f"All providers failed to meet the quality threshold. Returning best effort: {best_result.provider_used}")
            return best_result
            
        raise RuntimeError(f"All stem separation providers failed. Last error: {last_error}")

# Global service instance
stem_service = StemSeparationService()
