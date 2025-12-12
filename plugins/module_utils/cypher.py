"""
    Filename: ./module_utils/cypher.py
    Author: diederick de Buck (diederick.de.buck@platform-42.com)
    Date: 2025-10-26
    Version: 4.3.0
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
) -> Tuple[str, Dict[str, Any], str]:
    cypher_query_inline: str = cypher_query
    for key, value in cypher_params.items():
        cypher_query_inline = cypher_query_inline.replace(f"${key}", repr(value))
    return (cypher_query, cypher_params, cypher_query_inline)

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
) -> Tuple[str, Dict[str, Any], str]:
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
    module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:

    # retrieve module params
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    property_key: str = module_params[u_skel.JsonTKN.PROPERTY_KEY.value]

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
    module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:

    # retrieve module params
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    property_key: str = module_params[u_skel.JsonTKN.PROPERTY_KEY.value]

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
    module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:

    # retrieve module params
    base_label: str = module_params[u_skel.JsonTKN.BASE_LABEL.value]
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    entity_name: str = module_params[u_skel.JsonTKN.ENTITY_NAME.value]

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
    module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:

    # retrieve module params
    base_label: str = module_params[u_skel.JsonTKN.BASE_LABEL.value]
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    entity_name: str = module_params[u_skel.JsonTKN.ENTITY_NAME.value]

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
    module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:

    # retrieve module params
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    entity_name: str = module_params[u_skel.JsonTKN.ENTITY_NAME.value]

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
    is_bulk: bool,
    module_params: Dict[str, Any],
    properties: Optional[Dict[str, Any]] = None
) -> Tuple[str, Dict[str, Any], str]:

    # retrieve module params
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    entity_name: str = module_params[u_skel.JsonTKN.ENTITY_NAME.value]
    singleton: bool = module_params[u_skel.JsonTKN.SINGLETON.value]

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
        is_bulk=is_bulk,
        singleton=singleton,
        label=normalised_label,
        properties=normalised_properties
    )
    return query_build(cypher_query, cypher_params)

#
#   vertex_bulk_add:
#
#
#   returns:
#       List of tuples: (bulk_cypher_query, batch_bindings)
#       where bulk_cypher_query is the UNWIND template with rewritten queries
#       and batch_bindings is a list of dicts holding the parameters per vertex.
#
def vertex_bulk_add(
    vertex_results: List[Tuple[str, Dict[str, Any], str]],
    batch_size: int
) -> List[Tuple[str, Dict[str, Any]]]:
    batch = []

    # accumulate queries and bindings per batch
    for batch_start in range(0, len(vertex_results), batch_size):
        batch_slice = vertex_results[batch_start:batch_start + batch_size]
        batch_bindings = []

        # rewrite $param -> row.param
        for cypher_query, cypher_params, _ in batch_slice:
            rewritten_query = cypher_query
            for param in cypher_params.keys():
                rewritten_query = rewritten_query.replace(f"${param}", f"row.{param}")

            # store in batch_bindings (bindings per row)
            batch_bindings.append(cypher_params)

        primitive_query = rewritten_query
        bulk_query = u_cyph_q.CypherQuery.BULK_TEMPLATE.format(primitive_query=primitive_query)
        batch.append((bulk_query, {u_skel.JsonTKN.BATCH.value: batch_bindings}))

    return batch

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
    module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:

    # retrieve module params
    relation_type: str = module_params[u_skel.JsonTKN.TYPE.value]
    label_from: str = module_params[u_skel.JsonTKN.FROM.value][u_skel.JsonTKN.LABEL.value]
    entity_name_from: str = module_params[u_skel.JsonTKN.FROM.value][u_skel.JsonTKN.ENTITY_NAME.value]
    label_to: str = module_params[u_skel.JsonTKN.TO.value][u_skel.JsonTKN.LABEL.value]
    entity_name_to: str = module_params[u_skel.JsonTKN.TO.value][u_skel.JsonTKN.ENTITY_NAME.value]
    bi_directional: bool = module_params[u_skel.JsonTKN.BI_DIRECTIONAL.value]
    unique_key: str = module_params[u_skel.JsonTKN.UNIQUE_KEY.value]

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
    is_bulk: bool,
    module_params: Dict[str, Any],
    properties: Optional[Dict[str, Any]] = None
) -> Tuple[str, Dict[str, Any], str]:

    # retrieve module params
    relation_type: str = module_params[u_skel.JsonTKN.TYPE.value]
    label_from: str = module_params[u_skel.JsonTKN.FROM.value][u_skel.JsonTKN.LABEL.value]
    entity_name_from: str = module_params[u_skel.JsonTKN.FROM.value][u_skel.JsonTKN.ENTITY_NAME.value]
    label_to: str = module_params[u_skel.JsonTKN.TO.value][u_skel.JsonTKN.LABEL.value]
    entity_name_to: str = module_params[u_skel.JsonTKN.TO.value][u_skel.JsonTKN.ENTITY_NAME.value]
    bi_directional: bool = module_params[u_skel.JsonTKN.BI_DIRECTIONAL.value]
    unique_key: str = module_params[u_skel.JsonTKN.UNIQUE_KEY.value]

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
            is_bulk=is_bulk,
            label_from=normalised_label_from,
            label_to=normalised_label_to,
            relation_type=normalised_relation_type,
            properties=normalised_properties,
            unique_key=normalised_unique_key
        )
    else:
        cypher_query = u_cyph_q.cypher_edge_add(
            check_mode=check_mode,
            is_bulk=is_bulk,
            label_from=normalised_label_from,
            label_to=normalised_label_to,
            relation_type=normalised_relation_type,
            properties=normalised_properties,
            unique_key=normalised_unique_key
        )
    return query_build(cypher_query, cypher_params)

#
#   edge_bulk_add:
#
#   returns:
#       List of tuples: (bulk_cypher_query, batch_bindings)
#       where bulk_cypher_query is the UNWIND template with rewritten queries
#       and batch_bindings is a list of dicts holding the parameters per edge.
#
def edge_bulk_add(
    edge_results: List[Tuple[str, Dict[str, Any], str]],
    batch_size: int
) -> List[Tuple[str, Dict[str, Any]]]:
    batch = []

    # accumulate queries and bindings per batch
    for batch_start in range(0, len(edge_results), batch_size):
        batch_slice = edge_results[batch_start:batch_start + batch_size]
        batch_bindings = []

        # rewrite $param -> row.param
        for cypher_query, cypher_params, _ in batch_slice:
            rewritten_query = cypher_query
            for param in cypher_params.keys():
                rewritten_query = rewritten_query.replace(f"${param}", f"row.{param}")

            # store in batch_bindings (bindings per row)
            batch_bindings.append(cypher_params)

        primitive_query = rewritten_query
        bulk_query = u_cyph_q.CypherQuery.BULK_TEMPLATE.format(primitive_query=primitive_query)
        batch.append((bulk_query, {u_skel.JsonTKN.BATCH.value: batch_bindings}))

    return batch


#
#   query:
#       non destructive query.
#       protected by session.execute_read()
#
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
    normalised_parameters: Dict[str, Any] = dict(parameters.items())

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
    result_summary: ResultSummary = response.consume()
    return (data, result_summary)
