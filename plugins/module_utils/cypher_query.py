from strenum import StrEnum
from typing import Dict, Any, Optional

from . import skeleton as u_skel

#
#   Notes:
#   - cypher queries don't need values, they only require bindings
#   - bindings are derived from mandatory Json-tokens like entity_name whereas
#     optional bindings are derived from the keys from properties  
#   - added backticks for identifiers label, type and entity_name to prevent collision with reserved words in cypher
#   - cypher parameters passed on via YAML are checked in module-main to prevent injection
#   - usage of multiple f-strings to prevent annoying \n in triple quoted string
#   - delete of bi-directional relationship is subtle: 
#       (a)-[:TRACK]->(b) 
#       (b)-[:TRACK]->(a) 
#     is equivaluent to: 
#       (a)-[:TRACK]-(b)
#
class CypherQuery(StrEnum):
    SYM = """
        CALL dbms.components() YIELD name, versions RETURN versions[0] AS version
    """
    GRAPH_RESET = """
        MATCH (n) 
        DETACH DELETE n;
    """
    VERTEX_DEL = """
        MERGE (n:`{label}` {{entity_name: $entity_name}})
        DETACH DELETE n;
    """
    VERTEX_ADD = """
        MERGE (n:`{label}` {{entity_name: $entity_name}})
        {set_clause} 
        RETURN 
        id(n) AS node_id, 
        labels(n) AS labels, 
        n.entity_name AS entity_name;
    """
    EDGE_DEL = """ 
        MATCH (a:`{from_label}` {{ entity_name: $from_entity_name}})
        MATCH (b:`{to_label}` {{ entity_name: $to_entity_name}})
        MERGE (a)-[r:`{relation_type}`]->(b)
        DELETE r;
    """
    EDGE_DEL_BI = """ 
        MATCH (a:`{from_label}` {{ entity_name: $from_entity_name}})
        MATCH (b:`{to_label}` {{ entity_name: $to_entity_name}})
        MERGE (a)-[r:`{relation_type}`]-(b)
        DELETE r;
    """
    EDGE_ADD = """
        MATCH (a:`{from_label}` {{ entity_name: $from_entity_name}})
        MATCH (b:`{to_label}` {{ entity_name: $to_entity_name}})
        {set_clause}
        MERGE (a)-[r:`{relation_type}`]->(b)
        RETURN r;
    """
    EDGE_ADD_BI = """

    """

def cypher_graph_reset(
        check_mode: bool
) -> str:
    return CypherQuery.SYM.value if check_mode else CypherQuery.GRAPH_RESET.value

def cypher_vertex_del(
        label: str
) -> str:
    return CypherQuery.VERTEX_DEL.value.format(
        label=label
        )

def cypher_vertex_add(
    label: str,
    properties: Optional[Dict[str, Any]] = None
) -> str:
    set_clause = (
        f"SET n += {{{', '.join(f'{k}: ${k}' for k in properties)}}}" if properties else ""
    )        
    return CypherQuery.VERTEX_ADD.value.format(
        label=label, 
        set_clause=set_clause
        )

def cypher_edge_del(
        from_label: str,
        to_label: str,
        relation_type: str
) -> str:
    return CypherQuery.EDGE_DEL.value(
        from_label=from_label, 
        to_label=to_label, 
        relation_type=relation_type
        )

def cypher_edge_del_bi(
        from_label: str,
        to_label: str,
        relation_type: str
) -> str:
    return CypherQuery.EDGE_DEL_BI.value(
        from_label=from_label, 
        to_label=to_label, 
        relation_type=relation_type
        )

def cypher_edge_add(
        from_label: str,
        to_label: str,
        relation_type: str,
        properties: Optional[Dict[str, Any]] = None
) -> str:
    set_clause = (
        f"SET r += {{{', '.join(f'{k}: ${k}' for k in properties)}}}" if properties else ""
    )
    return CypherQuery.EDGE_ADD.value.format(
        from_label=from_label,
        to_label=to_label,
        set_clause=set_clause,
        relation_type=relation_type
    )
#    return (
#        f"MATCH (a:`{from_label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.FROM_ENTITY_NAME.value} }}), "
#        f"(b:`{to_label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.TO_ENTITY_NAME.value}  }}) "
#        f"MERGE (a)-[r:`{relation_type}`]->(b) "
#        f"{set_clause} "
#        f"RETURN "
#        f"{u_skel.JsonTKN.ID.value}(r) AS {u_skel.JsonTKN.REL_ID.value}, "
#        f"type(r) AS {u_skel.JsonTKN.RELATION_TYPE.value}, "
#        f"a.{u_skel.JsonTKN.ENTITY_NAME.value} AS {u_skel.JsonTKN.FROM_ENTITY_NAME.value}, "
#        f"b.{u_skel.JsonTKN.ENTITY_NAME.value} AS {u_skel.JsonTKN.TO_ENTITY_NAME.value}"
#    )

def cypher_edge_add_bi(
        from_label: str,
        to_label: str,
        relation_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
    set_clause_r1 = (
        f"SET r1 += {{{', '.join(f'{k}: ${k}' for k in properties)}}}" if properties else ""
    )
    set_clause_r2 = (
        f"SET r2 += {{{', '.join(f'{k}: ${k}' for k in properties)}}}" if properties else ""
    )
    return (
        f"MATCH "
        f"(a:`{from_label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.FROM_ENTITY_NAME.value} }}), "
        f"(b:`{to_label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.TO_ENTITY_NAME.value} }}) "
        f"MERGE (a)-[r1:`{relation_type}`]->(b) "
        f"{set_clause_r1} "
        f"MERGE (b)-[r2:`{relation_type}`]->(a) "
        f"{set_clause_r2} "
        f"RETURN "
        f"{u_skel.JsonTKN.ID.value}(r1) AS {u_skel.JsonTKN.REL1_ID.value}, "
        f"{u_skel.JsonTKN.ID.value}(r2) AS {u_skel.JsonTKN.REL2_ID.value}, "
        f"{u_skel.JsonTKN.TYPE.value}(r1) AS {u_skel.JsonTKN.RELATION_TYPE.value}, "
        f"a.{u_skel.JsonTKN.ENTITY_NAME.value} AS {u_skel.JsonTKN.FROM_ENTITY_NAME.value}, " 
        f"b.{u_skel.JsonTKN.ENTITY_NAME.value} AS {u_skel.JsonTKN.TO_ENTITY_NAME.value}"
    )