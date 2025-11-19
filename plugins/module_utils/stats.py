"""
    Filename: ./module_utils/stats.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 4.1.0
    Description: 
        NEO4J stats functions for bulk
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class EntitySummary:
    total: int = 0
    processed: int = 0
    nodes_created: int = 0
    nodes_deleted: int = 0
    relationships_created: int = 0
    relationships_deleted: int = 0
    labels_added: int = 0
    labels_removed: int = 0
    properties_set: int = 0
    errors: int = 0
    diagnostics: Optional[List[Dict[str, Any]]] = None

    def __post_init__(
        self
    ) -> None:
        if self.diagnostics is None:
            self.diagnostics = []

    def as_payload(
        self
    ) -> Dict[str, Any]:
        return asdict(self)

