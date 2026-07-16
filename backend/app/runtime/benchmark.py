from typing import List, Dict
import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import JobBenchmark
from app.runtime.registry import ProviderRegistry

class BenchmarkEngine:
    """
    Allows objective comparisons of different AI providers for the same task.
    """
    @staticmethod
    async def run_benchmark(db: AsyncSession, task_type: str, providers: List[str], test_input: Dict):
        results = []
        for provider_name in providers:
            if not await ProviderRegistry.validate_provider(provider_name):
                continue
                
            provider = ProviderRegistry.get_provider(provider_name)
            
            start_time = time.time()
            try:
                await provider.initialize()
                if await provider.validate(test_input):
                    prep = await provider.prepare(test_input)
                    out = await provider.run(prep)
                    await provider.publish_artifacts(out)
            except Exception as e:
                # Log failure
                pass
            finally:
                await provider.cleanup()
                
            duration = time.time() - start_time
            
            # Save benchmark metric
            metric = JobBenchmark(
                job_type=task_type,
                provider_name=provider_name,
                duration_sec=duration,
                quality_score=None # Requires human or objective algorithmic grading later
            )
            db.add(metric)
            await db.commit()
            
            results.append({"provider": provider_name, "duration": duration})
            
        return results
