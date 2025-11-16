"""
    Filename: ./module_utils/cypher.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 4.1.0
    Description: 
        Ansible module argument parsing and validation
"""
from typing import Dict, Any, Optional, Tuple, List
from neo4j import Transaction, ResultSummary, Result

from . import skeleton as u_skel
from . import cypher_query as u_cyph_q

#
#   Notes:
#   - vertex label must be capitalised - enforced (NEO4J advise)
#   - edge type must be uppercased - enforced (NEO4J advise)
#   - vertex name is set explicitly to entity_name - enforced (Ansible clarity)
#   - property keys are explicitly converted to lowercase JSON-keys to avoid duplicate properties - enforced
#   - property keys must be valid JSON and must comply to Neo4j rules - stronger enforcement than regular JSON keys
#   - implemented Ansible primitives return 3-tuple
#              cypher_query: str -> NEO4J query with only bindings
#             cypher_params: Dict[str, Any] -> NEO4J values for bindings
#       cypher_query_inline: str -> NEO4J query with substituted values for debugging in NEO4J console
#   - properties and parameters must be type-casted before usage
#

def query_build(
    cypher_query: str,
    cypher_params: Dict[str, Any]
)-> Tuple[str, Dict[str, Any], str]:
    cypher_query_inline: str = cypher_query
    for key, value in cypher_params.items():
        cypher_query_inline = cypher_query_inline.replace(f"${key}", repr(value))
    return cypher_query, cypher_params, cypher_query_inline

#
#   graph_reset:
#       removes vertex
#       returns a 3-tuple to be symmetric with other Ansible primitves
#
#   returns:
#       cypher_query -> cypher query with bindings
#       cypher_params -> values for bindings
#       cypher_query_inline -> cypher query with value substitution
#
def graph_reset(
    check_mode: bool
)-> Tuple[str, Dict[str, Any], str]:
    cypher_query: str = u_cyph_q.cypher_graph_reset(check_mode)
    cypher_params: Dict[str, Any] = {}
    return query_build(cypher_query, cypher_params)

#
#   contraint_del:
#       removes constraint based on name
#
#   returns:
#       cypher_query -> cypher query with bindings
#       cypher_params -> values for bindings
#       cypher_query_inline -> cypher query with value substitution
#
def constraint_del(
    check_mode: bool,
    label: str,
    property_key: str
) -> Tuple[str, Dict[str, Any], str]:

    # normalise
    normalised_label: str = label.capitalize()

    # cypher construction - values for bindings
    cypher_params: Dict[str, Any] = {}
    cypher_query: str = u_cyph_q.cypher_constraint_del(
        check_mode=check_mode,
        label=normalised_label,
        property_key=property_key
    )
    return query_build(cypher_query, cypher_params)

#
#   contraint_add:
#       adds unique index on given property
#
#   returns:
#       cypher_query -> cypher query with bindings
#       cypher_params -> values for bindings
#       cypher_query_inline -> cypher query with value substitution
#
def constraint_add(
    check_mode: bool,
    label: str,
    property_key: str
) -> Tuple[str, Dict[str, Any], str]:

    # normalise
    normalised_label: str = label.capitalize()

    # cypher construction - values for bindings
    cypher_params: Dict[str, Any] = {}
    cypher_query: str = u_cyph_q.cypher_constraint_add(
        check_mode=check_mode,
        label=normalised_label,
        property_key=property_key
    )
    return query_build(cypher_query, cypher_params)

#
#   label_del:
#       removes label from existing vertex
#
#   returns:
#       cypher_query -> cypher query with bindings
#       cypher_params -> values for bindings
#       cypher_query_inline -> cypher query with value substitution
#
def label_del(
    check_mode: bool,
    base_label: str,
    label: str,
    entity_name: str
) -> Tuple[str, Dict[str, Any], str]:

    # normalise
    normalised_base_label: str = base_label.capitalize()
    normalised_label: str = label.capitalize()

    # cypher construction - values for bindings
    cypher_params: Dict[str, Any] = {
        u_skel.JsonTKN.ENTITY_NAME.value: entity_name,
    }
    cypher_query: str = u_cyph_q.cypher_label_del(
        check_mode=check_mode,
        base_label=normalised_base_label,
        label_to_remove=normalised_label
    )
    return query_build(cypher_query, cypher_params)

#
#   label_add:
#       adds label to existing vertex
#
#   returns:
#       cypher_query -> cypher query with bindings
#       cypher_params -> values for bindings
#       cypher_query_inline -> cypher query with value substitution
#
def label_add(
    check_mode: bool,
    base_label: str,
    label: str,
    entity_name: str
) -> Tuple[str, Dict[str, Any], str]:

    # normalise
    normalised_base_label: str = base_label.capitalize()
    normalised_label: str = label.capitalize()

    # cypher construction - values for bindings
    cypher_params: Dict[str, Any] = {
        u_skel.JsonTKN.ENTITY_NAME.value: entity_name
    }
    cypher_query: str = u_cyph_q.cypher_label_add(
        check_mode=check_mode,
        base_label=normalised_base_label,
        label_to_create=normalised_label
    )
    return query_build(cypher_query, cypher_params)

#
#   vertex_del:
#       removes vertex
#
#   returns:
#       cypher_query -> cypher query with bindings
#       cypher_params -> values for bindings
#       cypher_query_inline -> cypher query with value substitution
#
def vertex_del(
    check_mode: bool,
    label: str,
    entity_name: str
) -> Tuple[str, Dict[str, Any], str]:

    # normalise
    normalised_label: str = label.capitalize()

    # cypher construction - values for bindings
    cypher_params: Dict[str, Any] = {
        u_skel.JsonTKN.ENTITY_NAME.value: entity_name
    }
    cypher_query: str = u_cyph_q.cypher_vertex_del(
        check_mode=check_mode,
        label=normalised_label
    )
    return query_build(cypher_query, cypher_params)

#
#   vertex_add:
#       creates vertex via MERGE operation (idempotence)
#
#   returns:
#       cypher_query -> cypher query with bindings
#       cypher_params -> values for bindings
#       cypher_query_inline -> cypher query with value substitution
#
def vertex_add(
    check_mode: bool,
    singleton: bool,
    label: str,
    entity_name: str,
    properties: Optional[Dict[str, Any]] = None,
) -> Tuple[str, Dict[str, Any], str]:

    # optionals
    if properties is None:
        properties = {}

    # normalise
    normalised_label: str = label.capitalize()
    normalised_properties: Dict[str, Any] = {key.lower(): value for key, value in properties.items()}

    # cypher construction - values for bindings
    cypher_params: Dict[str, Any] = {
        u_skel.JsonTKN.ENTITY_NAME.value: entity_name,
        **normalised_properties
    }
    cypher_query: str = u_cyph_q.cypher_vertex_add(
        check_mode=check_mode,
        singleton=singleton,
        label=normalised_label,
        properties=normalised_properties
    )
    return query_build(cypher_query, cypher_params)

#
#   edge_del:
#       removes (bi-directional) relationship if it exists
#
#   returns:
#       cypher_query -> cypher query with bindings
#       cypher_params -> values for bindings
#       cypher_query_inline -> cypher query with value substitution
#
def edge_del(
    check_mode: bool,
    relation_type: str,
    label_from: str,
    entity_name_from: str,
    label_to: str,
    entity_name_to: str,
    bi_directional: Optional[bool] = False,
    unique_key: Optional[str] = None
) -> Tuple[str, Dict[str, Any], str]:

    # normalise
    normalised_relation_type: str = relation_type.upper()
    normalised_label_from: str = label_from.capitalize()
    normalised_label_to: str = label_to.capitalize()
    normalised_unique_key: Optional[str] = None
    if unique_key:
        normalised_unique_key = unique_key.lower()

    # cypher construction - values for bindings
    cypher_params: Dict[str, Any] = {
        u_skel.JsonTKN.ENTITY_NAME_FROM.value: entity_name_from,
        u_skel.JsonTKN.ENTITY_NAME_TO.value: entity_name_to
    }
    cypher_query: str
    if bi_directional:
        cypher_query = u_cyph_q.cypher_edge_del_bi(
            check_mode=check_mode,
            label_from=normalised_label_from,
            label_to=normalised_label_to,
            relation_type=normalised_relation_type,
            unique_key=normalised_unique_key
        )
    else:
        cypher_query = u_cyph_q.cypher_edge_del(
            check_mode=check_mode,
            label_from=normalised_label_from,
            label_to=normalised_label_to,
            relation_type=normalised_relation_type,
            unique_key=normalised_unique_key
        )
    return query_build(cypher_query, cypher_params)

#
#   edge_add:
#       creates (bi-directional) relationship via MERGE operation (idempotence)
#
#   returns:
#       cypher_query -> cypher query with bindings
#       cypher_params -> values for bindings
#       cypher_query_inline -> cypher query with value substitution
#
def edge_add(
    check_mode: bool,
    relation_type: str,
    label_from: str,
    entity_name_from: str,
    label_to: str,
    entity_name_to: str,
    properties: Optional[Dict[str, Any]] = None,
    bi_directional: Optional[bool] = False,
    unique_key: Optional[str] = None
) -> Tuple[str, Dict[str, Any], str]:
    # optionals
    if properties is None:
        properties = {}

    # normalise
    normalised_relation_type: str = relation_type.upper()
    normalised_label_from: str = label_from.capitalize()
    normalised_label_to: str = label_to.capitalize()
    normalised_properties: Dict[str, Any] = {key.lower(): value for key, value in properties.items()}
    normalised_unique_key: Optional[str] = None
    if unique_key:
        normalised_unique_key = unique_key.lower()

    # cypher construction - values for bindings
    cypher_params: Dict[str, Any] = {
        u_skel.JsonTKN.ENTITY_NAME_FROM.value: entity_name_from,
        u_skel.JsonTKN.ENTITY_NAME_TO.value: entity_name_to,
        **normalised_properties
    }

    cypher_query: str
    if bi_directional:
        cypher_query = u_cyph_q.cypher_edge_add_bi(
            check_mode=check_mode,
            label_from=normalised_label_from,
            label_to=normalised_label_to,
            relation_type=normalised_relation_type,
            properties=normalised_properties,
            unique_key=normalised_unique_key
        )
    else:
        cypher_query = u_cyph_q.cypher_edge_add(
            check_mode=check_mode,
            label_from=normalised_label_from,
            label_to=normalised_label_to,
            relation_type=normalised_relation_type,
            properties=normalised_properties,
            unique_key=normalised_unique_key
        )
    return query_build(cypher_query, cypher_params)

#
#   query:
#       non destructive query.
#       protected by session.execute_read()
#   notes:
#       query is a difficult beast
#       - cypher is now defined outside the context of Ansible
#       - therefore we cannot apply enforcements like lowercase for keys
#       - In query, query defines the “API contract” itself; no schema or
#         object model exists outside the query. Therefore, no sanitising of parameters
#
#   returns:
#       cypher_query -> cypher query with bindings
#       cypher_params -> values for bindings
#       cypher_query_inline -> cypher query with value substitution
#
def query(
    cypher_query: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Tuple[str, Dict[str, Any], str]:
    # optionals
    if parameters is None:
        parameters = {}

    # normalise - no lowercase from raw-cypher, keep contract as is
    normalised_parameters: Dict[str, Any] = {key: value for key, value in parameters.items()}

    # cypher construction - values for bindings
    cypher_params: Dict[str, Any] = {
        **normalised_parameters
    }
    return query_build(cypher_query, cypher_params)

#
#   query_tx:
#       transactional wrapper to support session.execute_read()
#
#   returns:
#       data -> cypher response
#       summary -> cypher stats summary
#
def query_tx(
    tx: Transaction,
    cypher_query: str,
    cypher_params: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], ResultSummary]:
    response: Result = tx.run(cypher_query, cypher_params)
    data: List[Dict[str, Any]] = response.data()
    summary: ResultSummary = response.consume()
    return data, summary

def cypher_stats(
    summary: ResultSummary
) -> Dict[str, Any]:
    return {
        u_skel.JsonTKN.NODES_CREATED.value: summary.counters.nodes_created,
        u_skel.JsonTKN.NODES_DELETED.value: summary.counters.nodes_deleted,
        u_skel.JsonTKN.RELATIONSHIPS_CREATED.value: summary.counters.relationships_created,
        u_skel.JsonTKN.RELATIONSHIPS_DELETED.value: summary.counters.relationships_deleted,
        u_skel.JsonTKN.LABELS_ADDED.value: summary.counters.labels_added,
        u_skel.JsonTKN.LABELS_REMOVED.value: summary.counters.labels_removed,
        u_skel.JsonTKN.QUERY_TYPE.value: summary.query_type,
        u_skel.JsonTKN.PROPERTIES_SET.value: summary.counters.properties_set,
        u_skel.JsonTKN.CONSTRAINTS_ADDED.value: summary.counters.constraints_added,
        u_skel.JsonTKN.CONSTRAINTS_REMOVED.value: summary.counters.constraints_removed,
        }
