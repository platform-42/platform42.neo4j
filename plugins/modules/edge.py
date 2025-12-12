#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Filename: ./modules/edge.py
    Author: diederick de Buck (diederick.de.buck@platform-42.com)
    Date: 2025-10-05
    Version: 4.3.0
    Description: 
        Ansible module to create graph relationship (edge)
"""

# pylint: disable=import-error
from typing import Dict, Any, Tuple, List
from ansible.module_utils.basic import AnsibleModule

import ansible_collections.platform42.neo4j.plugins.module_utils.argument_spec as u_args
import ansible_collections.platform42.neo4j.plugins.module_utils.skeleton as u_skel
import ansible_collections.platform42.neo4j.plugins.module_utils.cypher as u_cypher
import ansible_collections.platform42.neo4j.plugins.module_utils.shared as u_shared
import ansible_collections.platform42.neo4j.plugins.module_utils.driver as u_driver
import ansible_collections.platform42.neo4j.plugins.module_utils.input as u_input
import ansible_collections.platform42.neo4j.plugins.module_utils.stats as u_stats

from neo4j import Driver, ResultSummary, Result, SummaryCounters
from neo4j.exceptions import Neo4jError

DOCUMENTATION = r'''
---
module: edge
short_description: Create or update a relationship (edge) between two vertices in Neo4j
version_added: "1.0.0"
author:
  - Diederick de Buck (diederick.de.buck@platform-42.com)
description:
  - This module creates a relationship (edge) between two existing vertices (nodes) in a Neo4j graph database.
  - It uses the official Neo4j Python driver and supports Aura (neo4j+s://) and self-hosted instances.
  - Both source and target nodes must already exist in the graph; the module will fail if either node cannot be found.
  - Relationship direction is always from C(source) → C(target).
notes:
  - The module uses a Cypher MERGE statement to ensure the relationship is created once between existing vertices.
  - For idempotent behavior, ensure source and target vertices are uniquely identifiable.
  - Relationship creation will fail if source or target nodes are missing.
  - edge-type follows uppercase naming style.
  - check_mode will validate all input parameters and returns version of Neo4j as proof that connection is established.
  - properties must be specified as a value/type pair, since Ansible turns everything into a string
'''

EXAMPLES = r'''
# Create a WORKS_AT relationship between Alice and Acme Corp
- name: "Create edge between Person and Company"
  platform42.neo4j.edge:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    type: WORKS_AT
    state: PRESENT
    from:
      label: "Person"
      entity_name: "alice"
    to:
      label: "Company"
      entity_name: "acme"
    properties:
      since: 
        value: 2020
        type: int
    unique_key: "since"

# Create a PURCHASED relationship without additional properties
- name: "Create PURCHASED edge"
  platform42.neo4j.edge:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    type: PURCHASED
    state: PRESENT
    from:
      label: "Customer"
      entity_name: "bob"
    to:
      label: "Product"
      entity_name: "widget-123"
'''

def edge_module(
    check_mode: bool,
    module_params: u_skel.ModuleParamsEdge,
    properties: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:
    relation_type: str = module_params[u_skel.JsonTKN.TYPE.value]
    label_from: str = module_params[u_skel.JsonTKN.FROM.value][u_skel.JsonTKN.LABEL.value]
    entity_name_from: str = module_params[u_skel.JsonTKN.FROM.value][u_skel.JsonTKN.ENTITY_NAME.value]
    label_to: str = module_params[u_skel.JsonTKN.TO.value][u_skel.JsonTKN.LABEL.value]
    entity_name_to: str = module_params[u_skel.JsonTKN.TO.value][u_skel.JsonTKN.ENTITY_NAME.value]
    bi_directional: bool = module_params[u_skel.JsonTKN.BI_DIRECTIONAL.value]
    state: str = module_params[u_skel.JsonTKN.STATE.value]
    unique_key: str = module_params[u_skel.JsonTKN.UNIQUE_KEY.value]
    edge_result: Tuple[str, Dict[str, Any], str]
    if u_skel.state_present(state):
        edge_result = u_cypher.edge_add(
            check_mode=check_mode,
            is_bulk=False,
            module_params=module_params,
            properties=properties
        )
        return edge_result
    edge_result = u_cypher.edge_del(
        check_mode=check_mode,
        module_params=module_params
    )
    return edge_result


def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_neo4j() | u_args.argument_spec_edge(),
        supports_check_mode=True
        )
    input_list: List[str] = [
        u_skel.JsonTKN.TYPE.value,
        u_skel.JsonTKN.FROM.value,
        u_skel.JsonTKN.TO.value,
        u_skel.JsonTKN.PROPERTIES.value,
        u_skel.JsonTKN.UNIQUE_KEY.value
        ]
    input_result: Tuple[bool, Dict[str, Any], Dict[str, Any]] = u_input.validate_inputs(
        cypher_input_list=input_list,
        module_params=module.params,
        supports_unique_key=False,
        supports_casting=True
        )
    result, casted_properties, diagnostics = input_result
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    driver: Driver = u_driver.get_driver(module.params)
    edge_result: Tuple[str, Dict[str, Any], str] = edge_module(
        module.check_mode,
        module.params,
        casted_properties
        )
    cypher_query, cypher_params, cypher_query_inline = edge_result
    payload: Dict[str, Any]
    try:
        with driver.session(database=module.params[u_skel.JsonTKN.DATABASE.value]) as session:
            response: Result = session.run(cypher_query, cypher_params)
            cypher_response: List[Dict[str, Any]] = [record.data() for record in list(response)]
            result_summary: ResultSummary = response.consume()
    except Neo4jError as e:
        payload = u_skel.payload_fail(cypher_query, cypher_params, cypher_query_inline, e)
        module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
    except Exception as e: # pylint: disable=broad-exception-caught
        payload = u_skel.payload_abend(e)
        module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
    finally:
        driver.close()
    payload = u_skel.payload_exit(
        cypher_query,
        cypher_params,
        cypher_query_inline,
        u_shared.serialize_neo4j(cypher_response),
        u_stats.cypher_stats(result_summary)
        )
    counters: SummaryCounters = result_summary.counters
    changed: bool = (counters.relationships_created > 0 or counters.relationships_deleted > 0)
    module.exit_json(**u_skel.ansible_exit(
        changed=changed,
        payload_key=module_name,
        payload=payload)
        )


if __name__ == '__main__':
    main()
