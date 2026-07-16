from typing import List, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.job import JobBenchmark
from app.runtime.registry import ProviderRegistry

class ProviderScoringSystem:
    """
    Analyzes historical statistics for providers to make intelligent scheduling decisions.
    """
    @staticmethod
    async def get_provider_stats(db: AsyncSession, task_type: str) -> List[Dict]:
        """
        Returns aggregate statistics (avg runtime, average quality) for a given task type.
        """
        query = select(
            JobBenchmark.provider_name,
            func.avg(JobBenchmark.duration_sec).label("avg_runtime"),
            func.avg(JobBenchmark.quality_score).label("avg_quality"),
            func.count(JobBenchmark.id).label("total_runs")
        ).where(JobBenchmark.job_type == task_type).group_by(JobBenchmark.provider_name)
        
        result = await db.execute(query)
        rows = result.all()
        
        stats = []
        for row in rows:
            stats.append({
                "provider": row.provider_name,
                "avg_runtime": float(row.avg_runtime) if row.avg_runtime else 0.0,
                "avg_quality": float(row.avg_quality) if row.avg_quality else 0.0,
                "total_runs": row.total_runs
            })
        return stats
        
    @staticmethod
    async def rank_providers(db: AsyncSession, task_type: str) -> List[str]:
        """
        Returns a ranked list of provider names based on historical quality and reliability.
        """
        stats = await ProviderScoringSystem.get_provider_stats(db, task_type)
        
        # Sort by quality primarily, then by lowest runtime
        # If no stats exist, we default to hardcoded priorities or all registered.
        if not stats:
            # Fallback to defaults
            if task_type == "stem_separation":
                return ["melband_roformer", "htdemucs"]
            return []
            
        stats.sort(key=lambda x: (-x["avg_quality"], x["avg_runtime"]))
        return [s["provider"] for s in stats]

class QualityComparator:
    """
    Automates decision making when comparing multiple outputs.
    """
    @staticmethod
    def evaluate_best_stem(results: List[Dict]) -> Dict:
        """
        Given multiple stem separation results, pick the one with the highest quality score.
        """
        if not results:
            return {}
            
        best = max(results, key=lambda x: x.get("quality_score", 0.0))
        return best
