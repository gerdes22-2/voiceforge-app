import os

with open("backend/app/orchestration/scoring.py", "w") as f:
    f.write("""from typing import List, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.job import JobBenchmark
from app.runtime.registry import ProviderRegistry

class ProviderScoringSystem:
    \"\"\"
    Analyzes historical statistics for providers to make intelligent scheduling decisions.
    \"\"\"
    @staticmethod
    async def get_provider_stats(db: AsyncSession, task_type: str) -> List[Dict]:
        \"\"\"
        Returns aggregate statistics (avg runtime, average quality) for a given task type.
        \"\"\"
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
        \"\"\"
        Returns a ranked list of provider names based on historical quality and reliability.
        \"\"\"
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
    \"\"\"
    Automates decision making when comparing multiple outputs.
    \"\"\"
    @staticmethod
    def evaluate_best_stem(results: List[Dict]) -> Dict:
        \"\"\"
        Given multiple stem separation results, pick the one with the highest quality score.
        \"\"\"
        if not results:
            return {}
            
        best = max(results, key=lambda x: x.get("quality_score", 0.0))
        return best
""")

os.makedirs("backend/app/providers/voice", exist_ok=True)
with open("backend/app/providers/voice/dataset_quality.py", "w") as f:
    f.write("""from typing import Dict, Any, List
from app.runtime.base import AIProvider
from app.runtime.profile import ResourceProfile

class DatasetQualityAnalyzer(AIProvider):
    \"\"\"
    Analyzes an entire Voice Dataset to provide a comprehensive health score
    before initiating Voice Training.
    \"\"\"
    
    def __init__(self):
        self._progress = 0.0
        
    @property
    def name(self) -> str:
        return "dataset_quality_analyzer"
        
    @property
    def profile(self) -> ResourceProfile:
        return ResourceProfile(
            gpu_required=False, # Mostly statistical and lightweight DSP
            min_vram_mb=0,
            min_ram_mb=4096,
            expected_runtime_sec=30,
            supports_cache=True,
            supports_resume=False,
            supports_cancellation=True
        )

    async def initialize(self) -> None:
        self._progress = 0.0

    async def validate(self, input_params: Dict[str, Any]) -> bool:
        if "dataset_items" not in input_params:
            raise ValueError("dataset_items required")
        return True

    async def prepare(self, input_params: Dict[str, Any]) -> Any:
        return input_params

    async def run(self, prepared_data: Any) -> Any:
        self._progress = 0.5
        items = prepared_data["dataset_items"]
        
        # Mock analysis
        speech_count = sum(1 for i in items if i.get("category") == "Speech")
        singing_count = sum(1 for i in items if i.get("category") == "Singing")
        total = len(items) or 1
        
        return {
            "speech_coverage": (speech_count / total) * 100,
            "singing_coverage": (singing_count / total) * 100,
            "noise_level": 5.0, # low is better
            "pitch_diversity": 85.0,
            "emotion_coverage": 70.0,
            "microphone_consistency": 95.0,
            "overall_health_score": 94.0
        }

    async def monitor(self) -> float:
        return self._progress

    async def cancel(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass

    async def publish_artifacts(self, run_result: Any) -> Dict[str, str]:
        return run_result
""")

with open("backend/app/providers/__init__.py", "a") as f:
    f.write("from app.providers.voice.dataset_quality import DatasetQualityAnalyzer\n")
    f.write("ProviderRegistry.register(DatasetQualityAnalyzer)\n")

