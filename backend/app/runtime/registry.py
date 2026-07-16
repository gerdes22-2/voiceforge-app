from typing import Dict, Type
import logging
from app.runtime.base import AIProvider

logger = logging.getLogger(__name__)

class ProviderRegistry:
    """
    Manages the availability and validation of AI providers.
    """
    _providers: Dict[str, Type[AIProvider]] = {}

    @classmethod
    def register(cls, provider_class: Type[AIProvider]):
        cls._providers[provider_class().name] = provider_class
        logger.info(f"Registered AI Provider: {provider_class().name}")

    @classmethod
    async def validate_provider(cls, name: str) -> bool:
        """
        Health Check -> Version Check -> Dependency Check -> GPU Check -> Ready
        """
        if name not in cls._providers:
            return False
            
        provider_instance = cls._providers[name]()
        profile = provider_instance.profile
        
        try:
            # 1. Health Check (mock)
            # 2. Dependency Check (mock)
            # 3. GPU Check (mock)
            if profile.gpu_required:
                # e.g., check torch.cuda.is_available() and free VRAM
                pass
                
            return True
        except Exception as e:
            logger.error(f"Provider validation failed for {name}: {e}")
            return False
            
    @classmethod
    def get_provider(cls, name: str) -> AIProvider:
        if name not in cls._providers:
            raise ValueError(f"Provider {name} not found.")
        return cls._providers[name]()
