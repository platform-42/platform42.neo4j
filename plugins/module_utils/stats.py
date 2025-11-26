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

    def __post_init__(
        self
    ) -> None:
        if self.diagnostics is None:
            self.diagnostics = []
        self.elapsed_time_msec = perf_counter()

    def as_payload(
        self
    ) -> Dict[str, Any]:
        return asdict(self)

    def stop_timer(
        self
    ) -> float:
        now: float = perf_counter()
        elapsed_msec: float = (now - self._start_time) * 1000
        self._start_time = now
        return elapsed_msec
