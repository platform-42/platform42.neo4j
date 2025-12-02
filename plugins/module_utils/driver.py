"""
    Filename: ./module_utils/driver.py
    Author: diederick de Buck (diederick.de.buck@platform-42.com)
    Date: 2025-11-04
    Version: 4.3.0
    Description: 
        Neo4j driver functions
"""
from typing import Dict, Any
from neo4j import GraphDatabase, Driver, basic_auth

from . import skeleton as u_skel


def get_neo4j_driver(
    db_uri: str,
    db_username: str,
    db_password: str
) -> Driver:
    return GraphDatabase.driver(
        uri=db_uri,
        auth=basic_auth(db_username, db_password)
    )


def get_driver(
    module_params: Dict[str, Any],
) -> Driver:
    db_uri: str = module_params[u_skel.JsonTKN.NEO4J_URI.value]
    db_username: str = module_params[u_skel.JsonTKN.USERNAME.value]
    db_password: str = module_params[u_skel.JsonTKN.PASSWORD.value]
    return get_neo4j_driver(
        db_uri=db_uri,
        db_username=db_username,
        db_password=db_password
    )
