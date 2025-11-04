from typing import Dict, Any, Optional, Tuple, List
from neo4j import Transaction, GraphDatabase, Driver, basic_auth, ResultSummary, Result

from . import skeleton as u_skel
from . import cypher as u_cypher

def get_driver(
    module_params: Dict[str, Any],
) -> Driver:
    db_uri: str = module_params[u_skel.JsonTKN.NEO4J_URI.value]
    db_username: str = module_params[u_skel.JsonTKN.USERNAME.value]
    db_password: str = module_params[u_skel.JsonTKN.PASSWORD.value]
    return u_cypher.get_neo4j_driver(
        db_uri=db_uri,
        db_username=db_username,
        db_password=db_password
    )