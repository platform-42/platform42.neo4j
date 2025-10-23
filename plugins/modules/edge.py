#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Filename: edge.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-05
    Version: 1.3.0
    Description: 
        Ansible module to create graph relationship (edge)
"""

# pylint: disable=import-error
from typing import Dict, Any, Tuple, List
from ansible.module_utils.basic import AnsibleModule

import ansible_collections.platform42.neo4j.plugins.module_utils.argument_spec as u_args
import ansible_collections.platform42.neo4j.plugins.module_utils.skeleton as u_skel
import ansible_collections.platform42.neo4j.plugins.module_utils.cypher as u_cypher
import ansible_collections.platform42.neo4j.plugins.module_utils.schema as u_schema

from neo4j import Driver, ResultSummary, Result

DOCUMENTATION = r'''
---
module: edge
short_description: Create or update a relationship (edge) between two vertices in Neo4j
version_added: "1.3.0"
author:
  - Diederick de Buck (diederick.de.buck@gmail.com)
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
  '''

EXAMPLES = r'''
# Create a WORKS_AT relationship between Alice and Acme Corp
- name: Create edge between Person and Company
  platform42.neo4j.edge:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    type: WORKS_AT
    from:
      label: "Person"
      entity_name: "alice"
    to:
      label: "Company"
      entity_name: "acme"
    properties:
      since: 2020

# Create a PURCHASED relationship without additional properties
- name: Create PURCHASED edge
  platform42.neo4j.edge:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    type: PURCHASED
    from:
      label: "Customer"
      entity_name: "bob"
    to:
      label: "Product"
      entity_name: "widget-123"
'''

def edge(
    check_mode: bool,
    module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:
    relation_type: str = module_params[u_skel.JsonTKN.TYPE.value]
    label_from: str = module_params[u_skel.JsonTKN.FROM.value][u_skel.JsonTKN.LABEL.value]
    entity_name_from: str = module_params[u_skel.JsonTKN.FROM.value][u_skel.JsonTKN.ENTITY_NAME.value]
    to_label: str = module_params[u_skel.JsonTKN.TO.value][u_skel.JsonTKN.LABEL.value]
    entity_name_to: str = module_params[u_skel.JsonTKN.TO.value][u_skel.JsonTKN.ENTITY_NAME.value]
    bi_directional: bool = module_params[u_skel.JsonTKN.BI_DIRECTIONAL.value]
    state: str = module_params[u_skel.JsonTKN.STATE.value]
    if u_skel.state_present(state):
        properties: Dict[str, Any] = module_params[u_skel.JsonTKN.PROPERTIES.value]
        return u_cypher.edge_add(
            check_mode,
            relation_type,
            label_from,
            entity_name_from,
            to_label,
            entity_name_to,
            properties,
            bi_directional
        )
    return u_cypher.edge_del(
        check_mode,
        relation_type,
        label_from,
        entity_name_from,
        to_label,
        entity_name_to,
        bi_directional
    )

def validate_cypher_inputs(
    module_params: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    result: bool
    diagnostics: Dict[str, Any]
    # validate edge-type against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.TYPE,
        module_params[u_skel.JsonTKN.TYPE.value]
        )
    if not result:
        return False, diagnostics
    # validate edge from-label against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.LABEL,
        module_params[u_skel.JsonTKN.FROM][u_skel.JsonTKN.LABEL.value]
        )
    if not result:
        return False, diagnostics
    # validate edge from-entity_name against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.ENTITY_NAME,
        module_params[u_skel.JsonTKN.FROM][u_skel.JsonTKN.ENTITY_NAME.value]
        )
    if not result:
        return False, diagnostics
    # validate edge to-label against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.LABEL,
        module_params[u_skel.JsonTKN.TO][u_skel.JsonTKN.LABEL.value]
        )
    if not result:
        return False, diagnostics
    # validate edge to-entity_name against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.ENTITY_NAME,
        module_params[u_skel.JsonTKN.TO][u_skel.JsonTKN.ENTITY_NAME.value]
        )
    if not result:
        return False, diagnostics
    key: str
    # validate edge properties against injection via JSON-key
    for key in module_params[u_skel.JsonTKN.PROPERTIES].keys():
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
        argument_spec=u_args.argument_spec_edge(),
        supports_check_mode=True
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
    cypher_query: str
    cypher_params: Dict[str, Any]
    cypher_query_inline: str
    cypher_query, cypher_params, cypher_query_inline = edge(
        module.check_mode,
        module.params
        )
    try:
        with driver.session(database=db_database) as session:
            response: Result = session.run(cypher_query, cypher_params)
            records = list(response)
            cypher_response: List[Dict[str, Any]] = [record.data() for record in records]
            summary: ResultSummary = response.consume()
    except Exception as e:
        module.fail_json(**u_skel.ansible_fail(diagnostics=f"{e}"))
    finally:
        driver.close()
    payload: Dict[str, Any] = {
        u_skel.JsonTKN.CYPHER_QUERY.value: u_skel.flatten_query(cypher_query),
        u_skel.JsonTKN.CYPHER_PARAMS.value: cypher_params,
        u_skel.JsonTKN.CYPHER_QUERY_INLINE.value: u_skel.flatten_query(cypher_query_inline),
        u_skel.JsonTKN.STATS.value: u_cypher.cypher_stats(summary),
        u_skel.JsonTKN.CYPHER_RESPONSE.value: cypher_response
        }
    state: str = module.params[u_skel.JsonTKN.STATE.value]
    relationships_changed: int = summary.counters.relationships_created if u_skel.state_present(state) else summary.counters.relationships_deleted
    changed: bool = relationships_changed > 0
    module.exit_json(**u_skel.ansible_exit(
        changed=changed,
        payload_key=module_name,
        payload=payload)
    )

if __name__ == '__main__':
    main()
