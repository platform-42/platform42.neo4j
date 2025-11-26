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
from time import perf_counter
from neo4j import ResultSummary

from . import skeleton as u_skel

def cypher_stats(
    result_summary: ResultSummary
) -> Dict[str, Any]:
    return {
        u_skel.JsonTKN.NODES_CREATED.value: result_summary.counters.nodes_created,
        u_skel.JsonTKN.NODES_DELETED.value: result_summary.counters.nodes_deleted,
        u_skel.JsonTKN.RELATIONSHIPS_CREATED.value: result_summary.counters.relationships_created,
        u_skel.JsonTKN.RELATIONSHIPS_DELETED.value: result_summary.counters.relationships_deleted,
        u_skel.JsonTKN.LABELS_ADDED.value: result_summary.counters.labels_added,
        u_skel.JsonTKN.LABELS_REMOVED.value: result_summary.counters.labels_removed,
        u_skel.JsonTKN.QUERY_TYPE.value: result_summary.query_type,
        u_skel.JsonTKN.PROPERTIES_SET.value: result_summary.counters.properties_set,
        u_skel.JsonTKN.CONSTRAINTS_ADDED.value: result_summary.counters.constraints_added,
        u_skel.JsonTKN.CONSTRAINTS_REMOVED.value: result_summary.counters.constraints_removed,
        }


from dataclasses import dataclass, field, asdict
from time import perf_counter
from typing import Any, Dict, List, Optional

@dataclass
class EntitySummary:
    total: int = 0
    elapsed_time_msec: float = 0
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

    # internal private field for timing
    _start_time: float = field(init=False, repr=False)

    def __post_init__(
        self
    ) -> None:
        if self.diagnostics is None:
            self.diagnostics = []
        self._start_time = perf_counter()

    def stop_timer(
        self
    ) -> None:
        end_time = perf_counter()
        self.elapsed_time_msec = (end_time - self._start_time) * 1000

    def as_payload(
        self
    ) -> Dict[str, Any]:
        end_time: float = perf_counter()
        self.elapsed_time_msec = (end_time - self._start_time) * 1000
        payload = {key: value for key, value in asdict(self).items() if not key.startswith("_")}
        return payload

