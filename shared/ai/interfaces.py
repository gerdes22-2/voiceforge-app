from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Awaitable
from .models import SeparationResult, QualityScore

class AIProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        pass

class StemSeparationProvider(AIProvider):
    @abstractmethod
    async def separate(
        self, 
        audio_file_path: str, 
        output_dir: str, 
        progress_callback: Callable[[float, str], Awaitable[None]] = None,
        **kwargs
    ) -> SeparationResult:
        """
        Separates the audio into stems.
        progress_callback: async function that accepts (progress_float, status_message)
        """
        pass

class AudioQualityAnalyzerProvider(AIProvider):
    @abstractmethod
    async def analyze_stems(
        self,
        vocals_path: str,
        instrumental_path: str
    ) -> QualityScore:
        """
        Analyzes the separated stems and returns a quality score.
        """
        pass
