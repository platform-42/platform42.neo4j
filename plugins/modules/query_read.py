#!/usr/bin/python
"""
    Filename: query_read.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-05
    Version: 1.3.0
    Description: 
        Ansible module to query a graph
"""

# pylint: disable=import-error
from typing import Dict, Any, Tuple
from ansible.module_utils.basic import AnsibleModule

import ansible_collections.platform42.neo4j.plugins.module_utils.argument_spec as u_args
import ansible_collections.platform42.neo4j.plugins.module_utils.skeleton as u_skel
import ansible_collections.platform42.neo4j.plugins.module_utils.cypher as u_cypher
import ansible_collections.platform42.neo4j.plugins.module_utils.schema as u_schema

from neo4j import Driver

DOCUMENTATION = r'''
---
module: query_read
short_description: Execute a read-only Cypher query in Neo4j and return results
version_added: "1.3.0"
author:
  - Diederick de Buck (diederick.de.buck@gmail.com)
description:
  - This module runs a Cypher query against a Neo4j database and returns the result data.
  - It is intended for read-only operations such as MATCH, RETURN, or CALL procedures that do not modify the graph.
  - The query parameters can be supplied as a dictionary, allowing for dynamic and safe query construction.
  - Supports Aura (neo4j+s://) and on-prem/self-hosted Neo4j instances.

seealso:
  - name: Neo4j Python Driver Documentation
    link: https://neo4j.com/docs/api/python-driver/current/
  - module: platform42.neo4j.query_write
    description: Execute write Cypher queries (CREATE, MERGE, DELETE)
  - module: platform42.neo4j.vertex
    description: Create or update Neo4j vertices
  - module: platform42.neo4j.edge
    description: Create or update Neo4j relationships

notes:
  - This module automatically serializes result data to JSON-safe format.
  - If the query returns Neo4j nodes or relationships, only their properties are returned.
  - The module will fail if a write operation is attempted (e.g., CREATE or MERGE).
  - check_mode it turned off, since this module is not able to modify any vertex, edge or attribute.
'''

EXAMPLES = r'''
# Read all Person nodes from Neo4j localhost
- name: Get all persons
  platform42.neo4j.query_read:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    cypher_query: >
      MATCH (p:Person) 
      RETURN p;

# Read filtered data with parameters from Neo4j Aura
- name: Find a specific person by name
  platform42.neo4j.query_read:
    neo4j_uri: "neo4j+s://<AURA_INSTANCEID>.databases.neo4j.io"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    cypher_query: > 
      MATCH (p:Person {name: $name}) 
      RETURN 
        p.name AS name
        p.age AS age
        p.gender AS gender;
    parameters:
      name: "Alice"
'''

def validate_cypher_inputs(
        module_params: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    result: bool
    diagnostics: Dict[str, Any]
    key: str
    # validate edge properties against injection via JSON-key
    for key in module_params[u_skel.JsonTKN.PARAMETERS.value].keys():
        result, diagnostics = u_schema.validate_pattern(
            u_schema.SchemaProperties.PROPERTY_KEYS,
            key
        )
        if not result:
            return False, diagnostics
    return True, {}

def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module:AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_query_read(),
        supports_check_mode=False
    )
    result: bool
    diagnostics: Dict[str, Any]
    result, diagnostics = validate_cypher_inputs(module.params)
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    db_uri: str = module.params[u_skel.JsonTKN.NEO4J_URI.value]
    db_database: str = module.params[u_skel.JsonTKN.DATABASE.value]
    db_username: str = module.params[u_skel.JsonTKN.USERNAME.value]
    db_password: str = module.params[u_skel.JsonTKN.PASSWORD.value]
    driver: Driver = u_cypher.get_neo4j_driver(
         db_uri=db_uri,
         db_username=db_username,
         db_password=db_password
    )
    query: str = module.params[u_skel.JsonTKN.QUERY.value]
    parameters: Dict[str, Any] = module.params[u_skel.JsonTKN.PARAMETERS.value]
    cypher_query: str
    cypher_params: Dict[str, Any]
    cypher_query_inline: str
    cypher_query, cypher_params, cypher_query_inline = u_cypher.query_read(
        query, 
        parameters
        )
    try:
        with driver.session(database=db_database) as session:
            data, summary = session.execute_read(u_cypher.query_read_tx, cypher_query, cypher_params)
    except Exception as e:
        module.fail_json(**u_skel.ansible_fail(diagnostics=f"{e}"))
    finally:
        driver.close()
    payload: Dict[str, Any] = {
        u_skel.JsonTKN.CYPHER_QUERY.value: u_skel.flatten_query(cypher_query),
        u_skel.JsonTKN.CYPHER_PARAMS.value: cypher_params,
        u_skel.JsonTKN.CYPHER_QUERY_INLINE.value: u_skel.flatten_query(cypher_query_inline),
        u_skel.JsonTKN.STATS.value: u_cypher.cypher_stats(summary),
        u_skel.JsonTKN.CYPHER_RESPONSE.value: data
    }
    module.exit_json(**u_skel.ansible_exit(
        changed=False,
        payload_key=module_name,
        payload=payload)
    )

if __name__ == '__main__':
    main()
