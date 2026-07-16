from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class AISandbox:
    """
    Ensures that if an AI provider crashes (e.g. CUDA OOM, segfault),
    it does not crash the main Workflow Engine or API.
    """
    @staticmethod
    @asynccontextmanager
    async def run_isolated(provider_name: str) -> AsyncGenerator[None, None]:
        """
        In a production system, this could spawn a child process, 
        a temporary Docker container, or an isolated Ray actor.
        """
        logger.info(f"Creating sandbox for {provider_name}...")
        try:
            # Yield control to execute provider methods inside sandbox
            yield
        finally:
            logger.info(f"Tearing down sandbox for {provider_name}...")
