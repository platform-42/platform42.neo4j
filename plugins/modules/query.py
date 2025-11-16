#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Filename: ./modules/query.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-05
    Version: 4.1.0
    Description: 
        Ansible module to query a graph
"""

# pylint: disable=import-error
from typing import Dict, Any, Tuple, Callable
from ansible.module_utils.basic import AnsibleModule

import ansible_collections.platform42.neo4j.plugins.module_utils.argument_spec as u_args
import ansible_collections.platform42.neo4j.plugins.module_utils.skeleton as u_skel
import ansible_collections.platform42.neo4j.plugins.module_utils.cypher as u_cypher
import ansible_collections.platform42.neo4j.plugins.module_utils.shared as u_shared
import ansible_collections.platform42.neo4j.plugins.module_utils.driver as u_driver
import ansible_collections.platform42.neo4j.plugins.module_utils.input as u_input

from neo4j import Driver
from neo4j.exceptions import Neo4jError

DOCUMENTATION = r'''
---
module: ./modules/query
short_description: Execute a read-only Cypher query in Neo4j and return results
version_added: "1.4.0"
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
  - properties must be specified as a value/type pair, since Ansible turns everything into a string
'''

EXAMPLES = r'''
# Read all Person nodes from Neo4j localhost
- name: Get all persons
  platform42.neo4j.query:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    query: |
      MATCH (p:Person) 
      RETURN p;

# Read filtered data with parameters from Neo4j Aura
- name: "Find a specific person by name"
  platform42.neo4j.query:
    neo4j_uri: "neo4j+s://<AURA_INSTANCEID>.databases.neo4j.io"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    query: | 
      MATCH (p:Person {entity_name: $name}) 
      RETURN 
        p.entity_name AS name
        p.age AS age
        p.gender AS gender;
    parameters:
      name: 
        value: "Alice"
        type: str
'''


def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_neo4j() | u_args.argument_spec_query(),
        supports_check_mode=False
        )
    input_result: Tuple[bool, Dict[str, Any], Dict[str, Any]] = u_input.validate_inputs(
        [u_skel.JsonTKN.PARAMETERS.value],
        module.params,
        False
        )
    result, casted_parameters, diagnostics = input_result
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
#    result, casted_parameters, diagnostics = u_input.type_casted_properties(
#        module.params[u_skel.JsonTKN.PARAMETERS.value]
#        )
#    if not result:
#        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    driver: Driver = u_driver.get_driver(module.params)
    query: str = module.params[u_skel.JsonTKN.QUERY.value]
    query_read_result: Tuple[str, Dict[str, Any], str] = u_cypher.query(
        query,
        casted_parameters
        )
    cypher_query, cypher_params, cypher_query_inline = query_read_result
    payload: Dict[str, Any]
    write_access: bool = module.params[u_skel.JsonTKN.WRITE_ACCESS.value]
    try:
        with driver.session(database=module.params[u_skel.JsonTKN.DATABASE.value]) as session:
            executor: Callable[
                [Callable[[Any, Any, Any], Any], str, Dict[str, Any]],
                Tuple[Any, Any]
                ] = session.execute_write if write_access else session.execute_read
            cypher_response, summary = executor(u_cypher.query_tx, cypher_query, cypher_params)
    except Neo4jError as e:
        payload = u_skel.payload_fail(cypher_query, cypher_params, cypher_query_inline, e)
        module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
    except Exception as e: # pylint: disable=broad-exception-caught
        payload = u_skel.payload_abend(cypher_query_inline, e)
        module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
    finally:
        driver.close()
    payload = u_skel.payload_exit(
        cypher_query,
        cypher_params,
        repr(cypher_query_inline),
        u_shared.serialize_neo4j(cypher_response),
        u_cypher.cypher_stats(summary),
        )
    module.exit_json(**u_skel.ansible_exit(
        changed=False,
        payload_key=module_name,
        payload=payload)
        )


if __name__ == '__main__':
    main()
