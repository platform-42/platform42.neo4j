#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,
# pylint: disable=line-too-long,too-many-arguments,too-many-locals
"""
    Filename: ./modules/graph_reset.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-05
    Version: 2.8.0
    Description: 
        Ansible module to reset graph database
"""

# pylint: disable=import-error
from typing import Dict, Any, List
from ansible.module_utils.basic import AnsibleModule

import ansible_collections.platform42.neo4j.plugins.module_utils.argument_spec as u_args
import ansible_collections.platform42.neo4j.plugins.module_utils.skeleton as u_skel
import ansible_collections.platform42.neo4j.plugins.module_utils.cypher as u_cypher
import ansible_collections.platform42.neo4j.plugins.module_utils.shared as u_shared
import ansible_collections.platform42.neo4j.plugins.module_utils.driver as u_driver

from neo4j import Driver, ResultSummary, Result

DOCUMENTATION = r'''
---
module: graph_reset
short_description: reset vertices and edges in Neo4j database
version_added: "1.2.0"
author:
  - Diederick de Buck (diederick.de.buck@gmail.com)
description:
  - This module removes nodes (vertex) and relations (edges) in a Neo4j graph database.
  - It uses the official Neo4j Python driver and supports Aura (neo4j+s://) and self-hosted databases.
  - The module expects parameters defined in the collection’s common argument specification utilities.
  - check_mode will validate all input parameters and returns version of Neo4j as proof that connection is established.
  - properties must be specified as a value/type pair, since Ansible turns everything into a string
  '''

EXAMPLES = r'''

# Reset database Neo4j localhost
- name: "Cleans up all vertices and edges in Neo4J graph database"
  platform42.neo4j.graph_reset:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"

# Reset database Neo4j Aura (cloud)
- name: "Cleans up all vertices and edges in Neo4J Aura (cloud) graph database"
  platform42.neo4j.graph_reset:
    neo4j_uri: "neo4j+s://<AURA_INSTANCEID>.databases.neo4j.io"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
'''

def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_graph_reset(),
        supports_check_mode=True
    )
    driver: Driver = u_driver.get_driver(module.params)
    cypher_query: str
    cypher_params: Dict[str, Any]
    cypher_query_inline: str
    cypher_query, cypher_params, cypher_query_inline = u_cypher.graph_reset(
        module.check_mode
        )
    payload: Dict[str, Any]
    try:
        with driver.session(database=module.params[u_skel.JsonTKN.DATABASE.value]) as session:
            response: Result = session.run(cypher_query)
            cypher_response: List[Dict[str, Any]] = [record.data() for record in list(response)]
            summary: ResultSummary = response.consume()
    except Exception as e:
        payload = u_skel.payload_fail(cypher_query, cypher_params, cypher_query_inline, e)
        module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
    finally:
        driver.close()
    payload = {
        u_skel.JsonTKN.CYPHER_QUERY.value: u_shared.flatten_query(cypher_query),
        u_skel.JsonTKN.CYPHER_PARAMS.value: cypher_params,
        u_skel.JsonTKN.CYPHER_QUERY_INLINE.value: u_shared.flatten_query(cypher_query_inline),
        u_skel.JsonTKN.STATS.value: u_cypher.cypher_stats(summary),
        u_skel.JsonTKN.CYPHER_RESPONSE.value: u_shared.serialize_neo4j(cypher_response)
    }
    module.exit_json(**u_skel.ansible_exit(
        changed=True,
        payload_key=module_name,
        payload=payload)
    )

if __name__ == '__main__':
    main()
