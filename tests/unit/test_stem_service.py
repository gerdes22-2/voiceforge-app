import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from shared.ai.models import SeparationResult, QualityScore
from worker.ai.services.stem_separation_service import StemSeparationService
from shared.ai.interfaces import StemSeparationProvider, AudioQualityAnalyzerProvider

class MockDemucs(StemSeparationProvider):
    @property
    def provider_name(self): return "demucs"
    @property
    def capabilities(self): return ["vocals", "instrumental"]
    
    async def separate(self, *args, **kwargs):
        return SeparationResult(stems={"vocals": "v.wav", "instrumental": "i.wav"}, provider_used="demucs")

class MockMelBand(StemSeparationProvider):
    @property
    def provider_name(self): return "melband"
    @property
    def capabilities(self): return ["vocals", "instrumental"]
    
    async def separate(self, *args, **kwargs):
        return SeparationResult(stems={"vocals": "v2.wav", "instrumental": "i2.wav"}, provider_used="melband")

class MockQuality(AudioQualityAnalyzerProvider):
    def __init__(self, scores):
        self.scores = scores
        self.call_count = 0
        
    @property
    def provider_name(self): return "mock_quality"
    @property
    def capabilities(self): return []
    
    async def analyze_stems(self, *args, **kwargs):
        score = self.scores[self.call_count]
        self.call_count += 1
        return score

@pytest.mark.asyncio
async def test_stem_service_success_first_try():
    # Setup
    quality = MockQuality([QualityScore(vocal_bleed=0, noise=0, clipping=0, artifacts=0, confidence_score=0.9)])
    service = StemSeparationService(quality_analyzer=quality)
    service.register_provider(MockDemucs())
    service.register_provider(MockMelBand())
    
    # Execute
    result = await service.separate("test.wav", "out", ["demucs", "melband"], min_acceptable_score=0.8)
    
    # Verify
    assert result.provider_used == "demucs"
    assert result.quality.confidence_score == 0.9

@pytest.mark.asyncio
async def test_stem_service_fallback():
    # Setup - First provider fails quality (0.5), second passes (0.9)
    quality = MockQuality([
        QualityScore(vocal_bleed=0, noise=0, clipping=0, artifacts=0, confidence_score=0.5),
        QualityScore(vocal_bleed=0, noise=0, clipping=0, artifacts=0, confidence_score=0.9)
    ])
    service = StemSeparationService(quality_analyzer=quality)
    service.register_provider(MockDemucs())
    service.register_provider(MockMelBand())
    
    # Execute
    result = await service.separate("test.wav", "out", ["demucs", "melband"], min_acceptable_score=0.8)
    
    # Verify fallback happened
    assert result.provider_used == "melband"
    assert result.quality.confidence_score == 0.9

@pytest.mark.asyncio
async def test_stem_service_all_fail_threshold_returns_best():
    # Setup - Both fail threshold, but demucs is better (0.7 vs 0.6)
    quality = MockQuality([
        QualityScore(vocal_bleed=0, noise=0, clipping=0, artifacts=0, confidence_score=0.7),
        QualityScore(vocal_bleed=0, noise=0, clipping=0, artifacts=0, confidence_score=0.6)
    ])
    service = StemSeparationService(quality_analyzer=quality)
    service.register_provider(MockDemucs())
    service.register_provider(MockMelBand())
    
    # Execute
    result = await service.separate("test.wav", "out", ["demucs", "melband"], min_acceptable_score=0.8)
    
    # Verify returns the best available (0.7)
    assert result.provider_used == "demucs"
    assert result.quality.confidence_score == 0.7
