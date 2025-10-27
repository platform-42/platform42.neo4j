# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,line-too-long
"""
    Filename: ./module_utils/cypher_query.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 2.3.0
    Description: 
        Cypher queries - returns string with bindings
"""
from typing import Dict, Any
from strenum import StrEnum

#
#   Notes:
#   - cypher queries doesn't need values, they only require bindings
#   - added backticks for identifiers label, type and entity_name to prevent collision with reserved words in cypher
#   - cypher parameters passed on via YAML are checked in module-main to prevent injection
#   - usage of multiple f-strings to prevent annoying \n in triple quoted string
#   - delete of bi-directional relationship is subtle:
#       (a)-[:TRACK]->(b)
#       (b)-[:TRACK]->(a)
#     is equivaluent to:
#       (a)-[:TRACK]-(b)
#   - set_clause_(r|n) translates properties into bindings
#       set_clause_r -> relationships (edges)
#       set_clause_n -> nodes (vertices)
#       amount: 5000 -> binding -> {amount: $amount}
#       cypher maps values to binding at query execution time (session.run)
#   - check_mode implements Ansible check_mode
#       check_mode validates all YAML-parameters for correctness
#       check_mode connects to Neo4j and returns version if connected
#
class CypherQuery(StrEnum):
    SIMULATION = """
        CALL dbms.components() YIELD versions 
        RETURN 
            versions[0] AS version
        ;
    """
    GRAPH_RESET = """
        MATCH (n) 
        DETACH DELETE n
        ;
    """
    VERTEX_DEL = """
        MERGE (n:`{label}` {{ entity_name: $entity_name }})
        DETACH DELETE n
        ;
    """
    VERTEX_ADD_UNIQUE = """
        MERGE (n:`{label}` {{ entity_name: $entity_name }})
        {set_clause} 
        RETURN 
            id(n) AS node_id, 
            labels(n) AS labels, 
            n.entity_name AS entity_name
        ;
    """
    VERTEX_ADD = """
        CREATE (n:`{label}` {{ entity_name: $entity_name }})
        {set_clause} 
        RETURN 
            id(n) AS node_id, 
            labels(n) AS labels, 
            n.entity_name AS entity_name
        ;
    """
    EDGE_DEL = """
        MATCH (a:`{label_from}` {{ entity_name: $entity_name_from }})
        MATCH (b:`{label_to}` {{ entity_name: $entity_name_to }})
        MERGE (a)-[r:`{relation_type}`]->(b)
        DELETE r
        ;
    """
    EDGE_DEL_BI = """
        MATCH (a:`{label_from}` {{ entity_name: $entity_name_from }})
        MATCH (b:`{label_to}` {{ entity_name: $entity_name_to }})
        MERGE (a)-[r:`{relation_type}`]-(b)
        DELETE r
        ;
    """
    EDGE_ADD = """
        MATCH (a:`{label_from}` {{ entity_name: $entity_name_from }})
        MATCH (b:`{label_to}` {{ entity_name: $entity_name_to }})
        MERGE (a)-[r:`{relation_type}`]->(b)
        {set_clause}
        RETURN 
            type(r) AS relation_type,
            a.entity_name AS entity_name_from, 
            b.entity_name AS entity_name_to
        ;
    """
    EDGE_ADD_BI = """
        MATCH (a:`{label_from}` {{ entity_name: $entity_name_from }})
        MATCH (b:`{label_to}` {{ entity_name: $entity_name_to }})
        MERGE (a)-[r1:`{relation_type}`]->(b)
        {set_clause_r1}
        MERGE (b)-[r2:`{relation_type}`]->(a)
        {set_clause_r2}
        RETURN  
            type(r1) AS relation_type,
            a.entity_name AS entity_name_from,
            b.entity_name AS entity_name_to
        ;
    """
    CONSTRAINT_DEL = """
        DROP CONSTRAINT {constraint_name} IF EXISTS
        ;
    """
    CONSTRAINT_ADD = """
        CREATE CONSTRAINT constraint_{label_id}_{property_id}_unique IF NOT EXISTS
        FOR (n:`{label}`)
        REQUIRE n.`{property}` IS UNIQUE
        ;
    """

def cypher_graph_reset(
    check_mode: bool
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.GRAPH_RESET.value)

def cypher_vertex_del(
    check_mode: bool,
    label: str
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.VERTEX_DEL.value.format(
        label=label
        )
    )

def cypher_vertex_add(
    check_mode: bool,
    unique: bool,
    label: str,
    properties: Dict[str, Any]
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    set_clause_n = f"SET n += {{{', '.join(f'{key}: ${key}' for key in properties.keys())}}}"
    if unique:
        return str(CypherQuery.VERTEX_ADD_UNIQUE.value.format(
            label=label,
            set_clause=set_clause_n
            )
        )
    return str(CypherQuery.VERTEX_ADD.value.format(
        label=label,
        set_clause=set_clause_n
        )
    )

def cypher_edge_del(
    check_mode: bool,
    label_from: str,
    label_to: str,
    relation_type: str
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.EDGE_DEL.value.format(
        label_from=label_from,
        label_to=label_to,
        relation_type=relation_type
        )
    )

def cypher_edge_del_bi(
    check_mode: bool,
    label_from: str,
    label_to: str,
    relation_type: str
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.EDGE_DEL_BI.value.format(
        label_from=label_from,
        label_to=label_to,
        relation_type=relation_type
        )
    )

def cypher_edge_add(
    check_mode: bool,
    label_from: str,
    label_to: str,
    relation_type: str,
    properties: Dict[str, Any]
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    set_clause_r = f"SET r += {{{', '.join(f'{key}: ${key}' for key in properties.keys())}}}"
    return str(CypherQuery.EDGE_ADD.value.format(
        label_from=label_from,
        label_to=label_to,
        set_clause=set_clause_r,
        relation_type=relation_type
        )
    )

def cypher_edge_add_bi(
    check_mode: bool,
    label_from: str,
    label_to: str,
    relation_type: str,
    properties: Dict[str, Any]
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    set_clause_r1 = f"SET r1 += {{{', '.join(f'{key}: ${key}' for key in properties.keys())}}}"
    set_clause_r2 = f"SET r2 += {{{', '.join(f'{key}: ${key}' for key in properties.keys())}}}"
    return str(CypherQuery.EDGE_ADD_BI.value.format(
        label_from=label_from,
        label_to=label_to,
        relation_type=relation_type,
        set_clause_r1=set_clause_r1,
        set_clause_r2=set_clause_r2
        )
    )

def cypher_constraint_del(
    check_mode: bool,
    label: str,
    property: str 
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    contraint_name: str = "constraint_{label_id}_{property_id}_unique".format(
        label_id=label.lower(),
        property_id=property.lower()
    )
    return str(CypherQuery.CONSTRAINT_DEL.value.format(
        constraint_name=contraint_name
        )
    )

def cypher_constraint_add(
    check_mode: bool,
    label: str,
    property: str 
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.CONSTRAINT_ADD.value.format(
        label_id=label.lower(),
        property_id=property.lower(),
        label=label,
        property=property
        )
    )
