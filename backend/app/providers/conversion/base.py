from abc import abstractmethod
from typing import Dict, Any
from app.runtime.base import AIProvider

class VoiceConversionProvider(AIProvider):
    """
    Abstract interface for Voice Conversion providers.
    """
    @abstractmethod
    async def extract_features(self, prepared_data: Any) -> Any:
        pass
        
    @abstractmethod
    async def convert(self, features_data: Any) -> Any:
        pass
