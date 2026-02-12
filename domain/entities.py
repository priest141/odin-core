from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class Alert:
    id: str
    raw_data: Dict[str, Any]
    enriched_data: Optional[Dict[str, Any]] = None

    def mark_enriched(self, enriched_data: Dict[str, Any]):
        self.enriched_data = enriched_data
