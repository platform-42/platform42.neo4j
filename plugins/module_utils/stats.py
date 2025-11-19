from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class VertexSummary:
    total: int = 0
    processed: int = 0
    created: int = 0
    deleted: int = 0
    errors: int = 0
    diagnostics: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.diagnostics is None:
            self.diagnostics = []

    def as_payload(self) -> Dict[str, Any]:
        """Return dict suitable for module exit_json payload."""
        return asdict(self)
    