from abc import abstractmethod
from typing import Dict, Any
from app.runtime.base import AIProvider

class VoiceTrainingProvider(AIProvider):
    """
    Abstract interface for Voice Model Training providers.
    """
    
    @abstractmethod
    async def train(self, features_data: Any) -> Any:
        pass
        
    @abstractmethod
    async def checkpoint(self) -> Any:
        pass
        
    @abstractmethod
    async def evaluate_loss(self) -> float:
        pass
