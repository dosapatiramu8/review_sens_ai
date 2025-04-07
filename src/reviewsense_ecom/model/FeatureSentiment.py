from dataclasses import dataclass, field
from typing import List


@dataclass
class FeatureSentiment:
    positive: List[str] = field(default_factory=list)
    negative: List[str] = field(default_factory=list)
