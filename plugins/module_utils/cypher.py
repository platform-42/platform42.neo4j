from neo4j import Transaction, GraphDatabase, Driver, basic_auth, ResultSummary, Result
from typing import Dict, Any, Optional, Tuple, List
from . import skeleton as u_skel
from . import cypher_query as u_cyph_q

#
#   Notes:
#   - vertex label must be capitalised - enforced (NEO4J advise)
#   - edge type must be uppercased - enforced (NEO4J advise)
#   - vertex name is set explicitly to entity_name - enforced (Ansible clarity) 
#   - property keys are explicitly converted to lowercase JSON-keys to avoid duplicate properties - enforced
#   - implemented Ansible primitives return 3-tuple
#              cypher_query: str -> NEO4J query with only bindings
#             cypher_params: Dict[str, Any] -> NEO4J values for bindings
#       cypher_query_inline: str -> NEO4J query with substituted values for debugging in NEO4J console
#

def get_neo4j_url(
        db_instance_id: str
        ) -> str:
    return f"neo4j+s://{db_instance_id}.databases.neo4j.io"

def get_neo4j_driver(
        db_instance_id: str,
        db_username: str, 
        db_password: str
        ) -> Driver:
    url: str = get_neo4j_url(db_instance_id)
    return GraphDatabase.driver(
        url,
        auth=basic_auth(db_username, db_password)
    )

def database_clean():
    cypher_query: str = f"MATCH (n) DETACH DELETE n"
    return cypher_query

def vertex_del(
        label: str, 
        entity_name: str
) -> Tuple[str, Dict[str, Any], str]:
    # normalise
    normalised_label: str = label.capitalize()

    # Params -> values without binding
    cypher_params: Dict[str, Any] = { 
        u_skel.JsonTKN.ENTITY_NAME.value: entity_name
    }

    # Parameterized query (safe for API)
    cypher_query: str = u_cyph_q.cypher_vertex_del(
        label=normalised_label
    )
    cypher_query_inline: str = cypher_query
    for key, value in cypher_params.items():
        cypher_query_inline = cypher_query_inline.replace(f"${key}", repr(value))
    return cypher_query, cypher_params, cypher_query_inline

def vertex_add(
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

    # Params -> values without binding
    cypher_params: Dict[str, Any] = { 
        u_skel.JsonTKN.ENTITY_NAME.value: entity_name, 
        **normalised_properties 
    }

    # Parameterized query (safe for API)
    cypher_query: str = u_cyph_q.cypher_vertex_add(
        label=normalised_label,
        properties=normalised_properties
    )
    cypher_query_inline: str = cypher_query
    for key, value in cypher_params.items():
        cypher_query_inline = cypher_query_inline.replace(f"${key}", repr(value))
    return cypher_query, cypher_params, cypher_query_inline

def edge_del(
        relation_type: str,
        from_label: str,
        from_entity_name: str,
        to_label: str,
        to_entity_name: str,
        bi_directional: bool = False
) -> Tuple[str, Dict[str, Any], str]:
    
    # normalise
    normalised_relation_type: str = relation_type.upper()
    normalised_from_label: str = from_label.capitalize()
    normalised_to_label: str = to_label.capitalize()

    # cypher construction
    cypher_params: Dict[str, Any] = {
        u_skel.JsonTKN.FROM_ENTITY_NAME.value: from_entity_name,
        u_skel.JsonTKN.TO_ENTITY_NAME.value: to_entity_name,
    }    
    if bi_directional:
        cypher_query = u_cyph_q.cypher_edge_del_bi(
            from_label=normalised_from_label,
            to_label=normalised_to_label,
            relation_type=normalised_relation_type
        )
    else:
        cypher_query = u_cyph_q.cypher_edge_del(
            from_label=normalised_from_label,
            to_label=normalised_to_label,
            relation_type=normalised_relation_type
        )
    cypher_query_inline: str = cypher_query
    for key, value in cypher_params.items():
        cypher_query_inline = cypher_query_inline.replace(f"${key}", repr(value))
    return cypher_query, cypher_params, cypher_query_inline

def edge_add(
        relation_type: str,
        from_label: str,
        from_entity_name: str,
        to_label: str,
        to_entity_name: str,
        properties: Optional[Dict[str, Any]] = None,
        bi_directional: bool = False,
    ) -> Tuple[str, Dict[str, Any], str]:

    # optionals
    if properties is None:
        properties = {}

    # normalise
    normalised_relation_type: str = relation_type.upper()
    normalised_from_label: str = from_label.capitalize()
    normalised_to_label: str = to_label.capitalize()
    normalised_properties: Dict[str, Any] = {key.lower(): value for key, value in properties.items()}

    # cypher construction
    cypher_params: Dict[str, Any] = {
        u_skel.JsonTKN.FROM_ENTITY_NAME.value: from_entity_name,
        u_skel.JsonTKN.TO_ENTITY_NAME.value: to_entity_name,
        **normalised_properties
    }
    if bi_directional:
        cypher_query = u_cyph_q.cypher_edge_add_bi(
            from_label=normalised_from_label,
            to_label=normalised_to_label,
            relation_type=normalised_relation_type,
            properties=normalised_properties
        )
    else:
        cypher_query = u_cyph_q.cypher_edge_add(
            from_label=normalised_from_label,
            to_label=normalised_to_label,
            relation_type=normalised_relation_type,
            properties=normalised_properties
        )
    cypher_query_inline: str = cypher_query
    for key, value in cypher_params.items():
        cypher_query_inline = cypher_query_inline.replace(f"${key}", repr(value))
    return cypher_query, cypher_params, cypher_query_inline

def query_read(
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
    
    # optionals
    if parameters is None:
        parameters = {}
    
    # normalise
    normalised_parameters: Dict[str, Any] = {key.lower(): value for key, value in parameters.items()}

    # cypher construction
    cypher_params: Dict[str, Any] = {
        **normalised_parameters
    }
    cypher_query: str = query
    cypher_query_inline: str = cypher_query
    for key, value in cypher_params.items():
        cypher_query_inline = cypher_query_inline.replace(f"${key}", repr(value))
    return cypher_query, cypher_params, cypher_query_inline 

def query_read_tx(tx: Transaction, cypher_query, cypher_params) -> Tuple[List[Dict[str, Any]], ResultSummary]:
    response: Result = tx.run(cypher_query, cypher_params)
    data: List[Dict[str, Any]] = response.data()
    summary: ResultSummary = response.consume()
    return data, summary

def cypher_stats(summary: ResultSummary) -> Dict[str, Any]:
    return {
        u_skel.JsonTKN.NODES_CREATED.value: summary.counters.nodes_created,
        u_skel.JsonTKN.NODES_DELETED.value: summary.counters.nodes_deleted,
        u_skel.JsonTKN.RELATIONSHIPS_CREATED.value: summary.counters.relationships_created,
        u_skel.JsonTKN.RELATIONSHIPS_DELETED.value: summary.counters.relationships_deleted,
        u_skel.JsonTKN.LABELS_ADDED.value: summary.counters.labels_added,
        u_skel.JsonTKN.LABELS_REMOVED.value: summary.counters.labels_removed,
        u_skel.JsonTKN.QUERY_TYPE.value: summary.query_type,
        u_skel.JsonTKN.PROPERTIES_SET.value: summary.counters.properties_set
        }
