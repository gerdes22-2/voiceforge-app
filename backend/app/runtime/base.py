from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.runtime.profile import ResourceProfile

class AIProvider(ABC):
    """
    Standard Execution Contract for all AI Providers (Stem Separation, Whisper, Voice Conversion, etc.)
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this provider (e.g., 'demucs_ht')"""
        pass
        
    @property
    @abstractmethod
    def profile(self) -> ResourceProfile:
        """Hardware and capability profile for scheduling"""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Setup initial state (e.g. load model architecture into memory)."""
        pass

    @abstractmethod
    async def validate(self, input_params: Dict[str, Any]) -> bool:
        """Validate that the input parameters and environment are correct before starting."""
        pass

    @abstractmethod
    async def prepare(self, input_params: Dict[str, Any]) -> Any:
        """Download files, slice audio, or prepare temp directories."""
        pass

    @abstractmethod
    async def run(self, prepared_data: Any) -> Any:
        """Execute the core AI workload. This might be blocking or async."""
        pass

    @abstractmethod
    async def monitor(self) -> float:
        """Return current progress (0.0 to 1.0)."""
        pass

    @abstractmethod
    async def cancel(self) -> None:
        """Gracefully terminate the `run` execution."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Free VRAM, delete temp files, remove Docker sandboxes."""
        pass

    @abstractmethod
    async def publish_artifacts(self, run_result: Any) -> Dict[str, str]:
        """Register outputs with the ArtifactManager and return URLs/Paths."""
        pass
