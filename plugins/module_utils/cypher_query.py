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

def cypher_graph_reset() -> str:
    return (
        f"MATCH (n) DETACH DELETE n"
    )

def cypher_vertex_del(
        label: str
) -> str:
    return (
        f"MERGE (n:`{label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.ENTITY_NAME.value} }}) "
        f"DETACH DELETE n;"
    )

def cypher_vertex_add(
    label: str,
    properties: Optional[Dict[str, Any]] = None
) -> str:
    set_clause = (
        f"SET n += {{{', '.join(f'{k}: ${k}' for k in properties)}}}" if properties else ""
    )        
    return (
        f"MERGE (n:`{label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.ENTITY_NAME.value} }}) "
        f"{set_clause} "
        f"RETURN "
        f"{u_skel.JsonTKN.ID.value}(n) AS {u_skel.JsonTKN.NODE_ID.value}, "
        f"{u_skel.JsonTKN.LABELS.value}(n) AS {u_skel.JsonTKN.LABELS.value}, "
        f"n.{u_skel.JsonTKN.ENTITY_NAME.value} AS {u_skel.JsonTKN.ENTITY_NAME.value}"
    )

def cypher_edge_del(
        from_label: str,
        to_label: str,
        relation_type: str
) -> str:
    return (
        f"MATCH (a:`{from_label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.FROM_ENTITY_NAME.value}}})-[r:`{relation_type}`]->(b:`{to_label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.TO_ENTITY_NAME.value} }})"
        f"DELETE r"
    )

def cypher_edge_del_bi(
        from_label: str,
        to_label: str,
        relation_type: str
) -> str:
    return (
        f"MATCH (a:`{from_label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.FROM_ENTITY_NAME.value}}})-[r:`{relation_type}`]-(b:`{to_label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.TO_ENTITY_NAME.value} }})"
        f"DELETE r"
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
    return (
        f"MATCH (a:`{from_label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.FROM_ENTITY_NAME.value} }}), "
        f"(b:`{to_label}` {{ {u_skel.JsonTKN.ENTITY_NAME.value}: ${u_skel.JsonTKN.TO_ENTITY_NAME.value}  }}) "
        f"MERGE (a)-[r:`{relation_type}`]->(b) "
        f"{set_clause} "
        f"RETURN "
        f"{u_skel.JsonTKN.ID.value}(r) AS {u_skel.JsonTKN.REL_ID.value}, "
        f"type(r) AS {u_skel.JsonTKN.RELATION_TYPE.value}, "
        f"a.{u_skel.JsonTKN.ENTITY_NAME.value} AS {u_skel.JsonTKN.FROM_ENTITY_NAME.value}, "
        f"b.{u_skel.JsonTKN.ENTITY_NAME.value} AS {u_skel.JsonTKN.TO_ENTITY_NAME.value}"
    )

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