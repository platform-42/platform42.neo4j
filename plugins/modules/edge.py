#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Filename: ./modules/edge.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-05
    Version: 3.1.0
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
import ansible_collections.platform42.neo4j.plugins.module_utils.shared as u_shared
import ansible_collections.platform42.neo4j.plugins.module_utils.driver as u_driver
import ansible_collections.platform42.neo4j.plugins.module_utils.input as u_input

from neo4j import Driver, ResultSummary, Result, SummaryCounters
from neo4j.exceptions import Neo4jError

DOCUMENTATION = r'''
---
module: edge
short_description: Create or update a relationship (edge) between two vertices in Neo4j
version_added: "1.0.0"
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

def edge(
    check_mode: bool,
    module_params: Dict[str, Any],
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
    if u_skel.state_present(state):
        return u_cypher.edge_add(
            check_mode,
            relation_type,
            label_from,
            entity_name_from,
            label_to,
            entity_name_to,
            properties,
            bi_directional,
            unique_key
        )
    return u_cypher.edge_del(
        check_mode,
        relation_type,
        label_from,
        entity_name_from,
        label_to,
        entity_name_to,
        bi_directional,
        unique_key
    )

def validate_cypher_inputs(
    module_params: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    result: bool
    diagnostics: Dict[str, Any]

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

    # validate edge properties against injection via JSON-key
    properties: Dict[str, Any] = module_params[u_skel.JsonTKN.PROPERTIES.value]
    for key in properties.keys():
        result, diagnostics = u_schema.validate_pattern(
            u_schema.SchemaProperties.PROPERTY_KEYS,
            key
        )
        if not result:
            return False, diagnostics

    # validate unique key if available
    unique_key: str = module_params[u_skel.JsonTKN.UNIQUE_KEY.value]
    if unique_key:
        result, diagnostics = u_schema.validate_pattern(
            u_schema.SchemaProperties.PROPERTY_KEY,
            module_params[u_skel.JsonTKN.UNIQUE_KEY.value]
            )
        if not result:
            return False, diagnostics

    # validate unique key against set of property keys
        normalized_property_keys = [key.strip().lower() for key in properties.keys()]
        if unique_key.strip().lower() not in normalized_property_keys:
            diagnostics = {u_skel.JsonTKN.ERROR_MSG: f"unique_key '{unique_key}' not found in properties"}
            return False, diagnostics
    return True, {}

def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_neo4j() | u_args.argument_spec_edge(),
        supports_check_mode=True
        )
    result, diagnostics = validate_cypher_inputs(module.params)
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    result, diagnostics = u_input.validate_cypher_inputs(
        [u_skel.JsonTKN.TYPE.value
         ],
        module.params
        )
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    result, casted_properties, diagnostics = u_shared.validate_optionals(module.params[u_skel.JsonTKN.PROPERTIES.value])
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    driver: Driver = u_driver.get_driver(module.params)
    edge_result: Tuple[str, Dict[str, Any], str] = edge(
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
            summary: ResultSummary = response.consume()
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
        cypher_query_inline,
        u_shared.serialize_neo4j(cypher_response),
        u_cypher.cypher_stats(summary)
        )
    state: str = module.params[u_skel.JsonTKN.STATE.value]
    counters: SummaryCounters = summary.counters
    relationships_changed: int = counters.relationships_created if u_skel.state_present(state) else counters.relationships_deleted
    changed: bool = relationships_changed > 0
    module.exit_json(**u_skel.ansible_exit(
        changed=changed,
        payload_key=module_name,
        payload=payload)
        )

if __name__ == '__main__':
    main()
