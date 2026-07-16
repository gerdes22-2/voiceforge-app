from pydantic import BaseModel
from typing import Dict, Optional, List

class QualityScore(BaseModel):
    vocal_bleed: float
    noise: float
    clipping: float
    artifacts: float
    confidence_score: float

class SeparationResult(BaseModel):
    stems: Dict[str, str]
    quality: Optional[QualityScore] = None
    provider_used: str
    metadata: Dict[str, str] = {}
