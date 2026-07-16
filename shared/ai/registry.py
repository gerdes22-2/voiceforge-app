from typing import Dict, Type, Optional
from .interfaces import AIProvider, StemSeparationProvider, VoiceConversionProvider

class AIProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, AIProvider] = {}
        
    def register(self, provider: AIProvider):
        self._providers[provider.provider_name] = provider
        
    def get_provider(self, name: str) -> Optional[AIProvider]:
        return self._providers.get(name)
        
    def get_stem_separator(self, name: str) -> Optional[StemSeparationProvider]:
        provider = self.get_provider(name)
        if isinstance(provider, StemSeparationProvider):
            return provider
        return None
        
    def get_voice_converter(self, name: str) -> Optional[VoiceConversionProvider]:
        provider = self.get_provider(name)
        if isinstance(provider, VoiceConversionProvider):
            return provider
        return None

# Global registry instance
ai_registry = AIProviderRegistry()
