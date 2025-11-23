"""
    Filename: ./module_utils/cypher_query.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 4.1.0
    Description: 
        Cypher queries - returns string with bindings
"""
from typing import Dict, Any, Optional
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
#       cypher, maps values to binding at query execution time (session.run)
#   - check_mode implements Ansible check_mode
#       check_mode validates all YAML-parameters for correctness
#       check_mode connects to Neo4j and returns version if connected
#   - set_relation_predicate -> ability to have duplicate relationships based on property
#       validates if the unique_key is part of a property_keys
#       if part, the value of the binding is already in place and therefore
#       ${unique_key} doesn't need any conversion whatsoever. It points already to the type-casted
#       property-value
#
#       so if unique_key contains "line", its binding will be "$line" and its value
#       is a guaranteed typecasted property that exists in cypher_params.
#       no duplication, just reuse of existing validated key
#

class RelationType(StrEnum):
    NODE = "n"
    RELATION = "r"
    RELATION_BI_1 = "r1"
    RELATION_BI_2 = "r2"

class CypherQuery(StrEnum):
    BULK_TEMPLATE = """
        CALL {{
            WITH $batch AS batch
            UNWIND batch AS row
            CALL {{
                WITH row
                {primitive_query}
            }}
            RETURN 1
        }}
        RETURN 1
        ;
    """
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
        MATCH (n:`{label}` {{entity_name: $entity_name}})
        DETACH DELETE n
        ;
        """
    VERTEX_ADD_SINGLETON = """
        MERGE (n:`{label}` {{entity_name: $entity_name}})
        {set_clause} 
        RETURN 
            id(n) AS node_id, 
            labels(n) AS labels, 
            n.entity_name AS entity_name
        ;
        """
    VERTEX_BULK_ADD_SINGLETON = """
        MERGE (n:`{label}` {{entity_name: $entity_name}})
        {set_clause} 
        ;
        """
    VERTEX_ADD = """
        CREATE (n:`{label}` {{entity_name: $entity_name}})
        {set_clause} 
        RETURN 
            id(n) AS node_id, 
            labels(n) AS labels, 
            n.entity_name AS entity_name
        ;
        """
    VERTEX_BULK_ADD = """
        CREATE (n:`{label}` {{entity_name: $entity_name}})
        {set_clause} 
        ;
        """
    EDGE_DEL = """
        MATCH (a:`{label_from}` {{entity_name: $entity_name_from}})
        MATCH (b:`{label_to}` {{entity_name: $entity_name_to}})
        MATCH (a)-[r:`{relation_type}` {relation_predicate}]->(b)
        DELETE r
        ;
        """
    EDGE_DEL_BI = """
        MATCH (a:`{label_from}` {{entity_name: $entity_name_from}})
        MATCH (b:`{label_to}` {{entity_name: $entity_name_to}})
        MATCH (a)-[r:`{relation_type}` {relation_predicate}]-(b)
        DELETE r
        ;
        """
    EDGE_ADD = """
        MATCH (a:`{label_from}` {{entity_name: $entity_name_from}})
        MATCH (b:`{label_to}` {{entity_name: $entity_name_to}})
        MERGE (a)-[r:`{relation_type}` {relation_predicate}]->(b)
        {set_clause}
        RETURN 
            type(r) AS relation_type,
            a.entity_name AS entity_name_from, 
            b.entity_name AS entity_name_to
        ;
        """
    EDGE_BULK_ADD = """
        MATCH (a:`{label_from}` {{entity_name: $entity_name_from}})
        MATCH (b:`{label_to}` {{entity_name: $entity_name_to}})
        MERGE (a)-[r:`{relation_type}` {relation_predicate}]->(b)
        {set_clause}
        ;
        """
    EDGE_ADD_BI = """
        MATCH (a:`{label_from}` {{entity_name: $entity_name_from}})
        MATCH (b:`{label_to}` {{entity_name: $entity_name_to}})
        MERGE (a)-[r1:`{relation_type}` {relation_predicate}]->(b)
        {set_clause_r1}
        MERGE (b)-[r2:`{relation_type}` {relation_predicate}]->(a)
        {set_clause_r2}
        RETURN  
            type(r1) AS relation_type,
            a.entity_name AS entity_name_from,
            b.entity_name AS entity_name_to
        ;
        """
    EDGE_BULK_ADD_BI = """
        MATCH (a:`{label_from}` {{entity_name: $entity_name_from}})
        MATCH (b:`{label_to}` {{entity_name: $entity_name_to}})
        MERGE (a)-[r1:`{relation_type}` {relation_predicate}]->(b)
        {set_clause_r1}
        MERGE (b)-[r2:`{relation_type}` {relation_predicate}]->(a)
        {set_clause_r2}
        ;
        """
    CONSTRAINT_DEL = """
        DROP CONSTRAINT {constraint_name} IF EXISTS
        ;
        """
    CONSTRAINT_ADD = """
        CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
        FOR (n:`{label}`)
        REQUIRE n.`{property_key}` IS UNIQUE
        ;
        """
    LABEL_DEL ="""
        MATCH (n:`{base_label}` {{entity_name: $entity_name}})
        REMOVE n:`{label_to_remove}`
        RETURN 
            labels(n) AS labels
        ;    
        """
    LABEL_ADD ="""
        MATCH (n:`{base_label}` {{entity_name: $entity_name}})
        SET n:`{label_to_create}`
        RETURN 
            labels(n) AS labels
        ;    
        """

def set_clause(
    relation_type: str,
    properties: Dict[str, Any]
) -> str:
    return f"SET {relation_type} += {{{', '.join(f'{key}: ${key}' for key in properties.keys())}}}"


def set_relation_predicate(
    unique_key: Optional[str]
) -> str:
    return f"{{{unique_key}: ${unique_key}}}" if unique_key else ""


def set_constraint_name(
    label: str,
    property_key: str
) -> str:
    return f"constraint_{label.lower()}_{property_key.lower()}_unique"


def cypher_bulk(  
) -> None:
    pass

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
    is_bulk: bool,
    singleton: bool,
    label: str,
    properties: Dict[str, Any]
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    if singleton:
        if is_bulk:
            return str(CypherQuery.VERTEX_BULK_ADD_SINGLETON.value.format(
                label=label,
                set_clause=set_clause(RelationType.NODE.value, properties)
                )
            )
        return str(CypherQuery.VERTEX_ADD_SINGLETON.value.format(
            label=label,
            set_clause=set_clause(RelationType.NODE.value, properties)
            )
        )
    if is_bulk:
        return str(CypherQuery.VERTEX_BULK_ADD.value.format(
            label=label,
            set_clause=set_clause(RelationType.NODE.value, properties)
            )
        )
    return str(CypherQuery.VERTEX_ADD.value.format(
        label=label,
        set_clause=set_clause(RelationType.NODE.value, properties)
        )
    )


def cypher_edge_del(
    check_mode: bool,
    label_from: str,
    label_to: str,
    relation_type: str,
    unique_key: Optional[str] = None
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.EDGE_DEL.value.format(
        label_from=label_from,
        label_to=label_to,
        relation_type=relation_type,
        relation_predicate=set_relation_predicate(unique_key)
        )
    )


def cypher_edge_del_bi(
    check_mode: bool,
    label_from: str,
    label_to: str,
    relation_type: str,
    unique_key: Optional[str] = None
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.EDGE_DEL_BI.value.format(
        label_from=label_from,
        label_to=label_to,
        relation_type=relation_type,
        relation_predicate=set_relation_predicate(unique_key)
        )
    )


def cypher_edge_add(
    check_mode: bool,
    is_bulk: bool,
    label_from: str,
    label_to: str,
    relation_type: str,
    properties: Dict[str, Any],
    unique_key: Optional[str] = None
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    if is_bulk:
        return str(CypherQuery.EDGE_BULK_ADD.value.format(
            label_from=label_from,
            label_to=label_to,
            relation_type=relation_type,
            relation_predicate=set_relation_predicate(unique_key),
            set_clause=set_clause(RelationType.RELATION.value, properties)
            )
        )
    return str(CypherQuery.EDGE_ADD.value.format(
        label_from=label_from,
        label_to=label_to,
        relation_type=relation_type,
        relation_predicate=set_relation_predicate(unique_key),
        set_clause=set_clause(RelationType.RELATION.value, properties)
        )
    )

def cypher_edge_add_bi(
    check_mode: bool,
    is_bulk: bool,
    label_from: str,
    label_to: str,
    relation_type: str,
    properties: Dict[str, Any],
    unique_key: Optional[str] = None
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    if is_bulk:
        return str(CypherQuery.EDGE_BULK_ADD_BI.value.format(
            label_from=label_from,
            label_to=label_to,
            relation_type=relation_type,
            set_clause_r1=set_clause(RelationType.RELATION_BI_1.value, properties),
            set_clause_r2=set_clause(RelationType.RELATION_BI_2.value, properties),
            relation_predicate=set_relation_predicate(unique_key)
            )
        )
    return str(CypherQuery.EDGE_ADD_BI.value.format(
        label_from=label_from,
        label_to=label_to,
        relation_type=relation_type,
        set_clause_r1=set_clause(RelationType.RELATION_BI_1.value, properties),
        set_clause_r2=set_clause(RelationType.RELATION_BI_2.value, properties),
        relation_predicate=set_relation_predicate(unique_key)
        )
    )


def cypher_constraint_del(
    check_mode: bool,
    label: str,
    property_key: str
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.CONSTRAINT_DEL.value.format(
        constraint_name=set_constraint_name(
            label,
            property_key
            )
        )
    )


def cypher_constraint_add(
    check_mode: bool,
    label: str,
    property_key: str
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.CONSTRAINT_ADD.value.format(
        label=label,
        property_key=property_key,
        constraint_name=set_constraint_name(
            label,
            property_key
            )
        )
    )


def cypher_label_del(
    check_mode: bool,
    base_label: str,
    label_to_remove: str
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.LABEL_DEL.value.format(
        base_label=base_label,
        label_to_remove=label_to_remove
        )
    )


def cypher_label_add(
    check_mode: bool,
    base_label: str,
    label_to_create: str
) -> str:
    if check_mode:
        return str(CypherQuery.SIMULATION.value)
    return str(CypherQuery.LABEL_ADD.value.format(
        base_label=base_label,
        label_to_create=label_to_create
        )
    )
