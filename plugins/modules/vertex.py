#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,
# pylint: disable=line-too-long,too-many-arguments,too-many-locals
"""
    Filename: ./modules/vertex.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-05
    Version: 2.8.0
    Description: 
        Ansible module to create graph node (vertex)
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

from neo4j import Driver, ResultSummary, Result

DOCUMENTATION = r'''
---
module: vertex
short_description: Create or update a vertex (node) in Neo4j
version_added: "1.0.0"
author:
  - Diederick de Buck (diederick.de.buck@gmail.com)
description:
  - This module creates or updates a node (vertex) in a Neo4j graph database.
  - It uses the official Neo4j Python driver and supports Aura (neo4j+s://) and self-hosted databases.
  - The module expects parameters defined in the collection’s common argument specification utilities.
notes:
  - vertex-label follows capitalized naming style.
  - check_mode will validate all input parameters and returns version of Neo4j as proof that connection is established.
  - properties must be specified as a value/type pair, since Ansible turns everything into a string
'''

EXAMPLES = r'''

# Create a Person vertex (label) with entity_name "Ada" from Neo4j localhost
- name: "Create user, labelled as a Person Node"
  platform42.neo4j.vertex:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    label: "Person"
    state: PRESENT
    entity_name: "Ada"
    singleton: True
    properties:
      age: 
        value: 30
        type: int

# Create a Product vertex (label) with entity_name "Widget-123" from Neo4j Aura
- name: "Create a product vertex"
  platform42.neo4j.vertex:
    neo4j_uri: "neo4j+s://<AURA_INSTANCEID>.databases.neo4j.io"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    label: "Product"
    state: PRESENT
    entity_name: "Widget-123"
    singleton: True
    properties:
      sku: 
        value: "widget-123"
        type: str
      price: 
        value: 9.99
        type: float
'''

def vertex(
    check_mode: bool,
    module_params: Dict[str, Any],
    properties: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    entity_name: str =module_params[u_skel.JsonTKN.ENTITY_NAME.value]
    state: str = module_params[u_skel.JsonTKN.STATE.value]
    singleton: bool = module_params[u_skel.JsonTKN.SINGLETON.value]
    if u_skel.state_present(state):
        return u_cypher.vertex_add(
            check_mode,
            singleton,
            label,
            entity_name,
            properties
            )
    return u_cypher.vertex_del(
        check_mode,
        label,
        entity_name
        )

def validate_cypher_inputs(
    module_params: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    result: bool
    diagnostics: Dict[str, Any]
    # validate vertex Label against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.LABEL,
        module_params[u_skel.JsonTKN.LABEL.value]
        )
    if not result:
        return False, diagnostics
    # validate vertex name against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.ENTITY_NAME,
        module_params[u_skel.JsonTKN.ENTITY_NAME.value]
        )
    if not result:
        return False, diagnostics
    key: str
    # validate vertex properties against injection via JSON-key
    for key in module_params[u_skel.JsonTKN.PROPERTIES.value].keys():
        result, diagnostics = u_schema.validate_pattern(
            u_schema.SchemaProperties.PROPERTY_KEYS,
            key
        )
        if not result:
            return False, diagnostics
    return True, {}

def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_vertex(),
        supports_check_mode=True
    )
    result: bool
    diagnostics: Dict[str, Any]
    result, diagnostics = validate_cypher_inputs(module.params)
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    result, casted_properties, diagnostics = u_shared.validate_optionals(
        module.params[u_skel.JsonTKN.PROPERTIES.value]
        )
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    driver: Driver = u_driver.get_driver(module.params)
    cypher_query: str
    cypher_params: Dict[str, Any]
    cypher_query_inline: str
    cypher_query, cypher_params, cypher_query_inline = vertex(
        module.check_mode,
        module.params,
        casted_properties
        )
    payload: Dict[str, Any]
    try:
        with driver.session(database=module.params[u_skel.JsonTKN.DATABASE.value]) as session:
            response: Result = session.run(cypher_query, cypher_params)
            cypher_response: List[Dict[str, Any]] = [record.data() for record in list(response)]
            summary: ResultSummary = response.consume()
    except Exception as e:
        payload = u_skel.payload_fail(cypher_query, cypher_params, cypher_query_inline, e)
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
    nodes_changed: int = summary.counters.nodes_created if u_skel.state_present(state) else summary.counters.nodes_deleted
    changed: bool = nodes_changed > 0
    module.exit_json(**u_skel.ansible_exit(
        changed=changed,
        payload_key=module_name,
        payload=payload)
        )

if __name__ == '__main__':
    main()
