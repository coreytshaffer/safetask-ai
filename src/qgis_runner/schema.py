from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class MapRecipe:
    id: str
    name: str
    description: str
    layers: List[str]
    default_extent: Dict[str, float]
    approved_uses: List[str]
    requires_review_for_public: bool


@dataclass
class MapExportMetadata:
    recipe_id: str
    timestamp: str
    center_coordinates: str
    exported_files: List[str]
    harness_decision: str
    warnings: List[str] = field(default_factory=list)
