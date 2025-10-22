#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Filename: graph_reset.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-05
    Version: 1.0
    Description: 
        Ansible module to reset graph database
"""
# pylint: disable=import-error
from typing import Dict, Any, List
from ansible.module_utils.basic import AnsibleModule

import ansible_collections.platform42.neo4j.plugins.module_utils.argument_spec as u_args
import ansible_collections.platform42.neo4j.plugins.module_utils.skeleton as u_skel
import ansible_collections.platform42.neo4j.plugins.module_utils.cypher as u_cypher

from neo4j import Driver, ResultSummary, Result

DOCUMENTATION = r'''
---
module: graph_reset
short_description: reset vertices and edges in Neo4j database
version_added: "1.0.0"
author:
  - Diederick de Buck (diederick.de.buck@gmail.com)
description:
  - This module removes nodes (vertex) and relations (edges) in a Neo4j graph database.
  - It uses the official Neo4j Python driver and supports Aura (neo4j+s://) and self-hosted databases.
  - The module expects parameters defined in the collection’s common argument specification utilities.
'''

EXAMPLES = r'''

# Reset database
- name: cleans up all vertices and edges in Neo4J graph database
  platform42.neo4j.graph_reset:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
'''

def main():
    module_name = u_skel.file_splitext(__file__)
    module = AnsibleModule(
        argument_spec=u_args.argument_spec_graph_reset(),
        supports_check_mode=False
    )
    db_uri: str = module.params[u_skel.JsonTKN.NEO4J_URI.value]
    db_database: str = module.params[u_skel.JsonTKN.DATABASE.value]
    db_username: str = module.params[u_skel.JsonTKN.USERNAME.value]
    db_password: str = module.params[u_skel.JsonTKN.PASSWORD.value]
    driver: Driver = u_cypher.get_neo4j_driver(
         db_uri=db_uri,
         db_username=db_username,
         db_password=db_password
    )
    cypher_query: str
    cypher_params: Dict[str, Any]
    cypher_query_inline: str
    cypher_query, cypher_params, cypher_query_inline = u_cypher.graph_reset()
    try:
        with driver.session(database=db_database) as session:
            response: Result = session.run(cypher_query)
            records = list(response)
            cypher_response: List[Dict[str, Any]] = [record.data() for record in records]
            summary: ResultSummary = response.consume()            
    except Exception as e:
        module.fail_json(**u_skel.ansible_fail(diagnostics=f"{e}"))
    finally:
        driver.close()
    summary: ResultSummary = response.consume()
    payload: Dict[str, Any] = {
        u_skel.JsonTKN.CYPHER_QUERY.value: cypher_query,
        u_skel.JsonTKN.CYPHER_PARAMS.value: cypher_params,
        u_skel.JsonTKN.CYPHER_QUERY_INLINE.value: cypher_query_inline,
        u_skel.JsonTKN.STATS.value: u_cypher.cypher_stats(summary),
        u_skel.JsonTKN.CYPHER_RESPONSE.value: cypher_response
    }
    module.exit_json(**u_skel.ansible_exit(
        changed=True,
        payload_key=module_name,
        payload=payload)
    )

if __name__ == '__main__':
    main()
