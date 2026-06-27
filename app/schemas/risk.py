from typing import List, Literal

from pydantic import BaseModel


class RiskOut(BaseModel):
    score: int
    level: Literal["LOW", "MEDIUM", "HIGH"]
    reasons: List[str]
