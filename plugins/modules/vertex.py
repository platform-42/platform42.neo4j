#!/usr/bin/python
"""
    Filename: vertex.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-05
    Version: 1.0
    Description: 
        Ansible module to create graph node (vertex)
"""

# pylint: disable=import-error
from typing import Dict, Any, Tuple
from ansible.module_utils.basic import AnsibleModule

import ansible_collections.platform42.neo4j.plugins.module_utils.argument_spec as u_args
import ansible_collections.platform42.neo4j.plugins.module_utils.skeleton as u_skel
import ansible_collections.platform42.neo4j.plugins.module_utils.cypher as u_cypher
import ansible_collections.platform42.neo4j.plugins.module_utils.schema as u_schema

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
  - vertex-label follows capitalized naming style
'''

EXAMPLES = r'''

# Create a Person vertex (label) with entity_name "Ada" 
- name: create user, labelled as a "Person" Node
  platform42.neo4j.vertex:
    instance_id: "abcdef12"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    label: "Person"
    entity_name: "Ada"
    properties:
      age: 30

# Create a Product vertex (label) with entity_name "Widget-123"
- name: Create a product vertex
  platform42.neo4j.vertex:
    instance_id: "abcdef12"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    label: "Product"
    entity_name: "Widget-123"
    properties:
      sku: "widget-123"
      price: 9.99
'''

def vertex(
        module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    entity_name: str =module_params[u_skel.JsonTKN.ENTITY_NAME.value]
    state: str = module_params[u_skel.JsonTKN.STATE.value]
    if u_skel.state_present(state):
        properties: Dict[str, Any] = module_params[u_skel.JsonTKN.PROPERTIES.value]
        return u_cypher.vertex_add(
            label,
            entity_name,
            properties,
            )
    return u_cypher.vertex_del(
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
        u_schema.SchemaProperties.LABEL.value,
        module_params[u_skel.JsonTKN.LABEL.value]
        )
    if not result:
        return False, diagnostics
    # validate vertex name against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.ENTITY_NAME.value,
        module_params[u_skel.JsonTKN.ENTITY_NAME.value]
        )
    if not result:
        return False, diagnostics
    key: str
    # validate vertex properties against injection via JSON-key
    for key in module_params[u_skel.JsonTKN.PROPERTIES.value].keys():
        result, diagnostics = u_schema.validate_pattern(
            u_schema.SchemaProperties.PROPERTY_KEYS.value,
            key
        )
        if not result:
            return False, diagnostics
    return True, {}

def main():
    module_name = u_skel.file_splitext(__file__)
    module = AnsibleModule(
        argument_spec=u_args.argument_spec_vertice(),
        supports_check_mode=False
    )
    result: bool
    diagnostics: Dict[str, Any]
    result, diagnostics = validate_cypher_inputs(module.params)
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    db_instance_id: str = module.params[u_skel.JsonTKN.INSTANCE_ID.value]
    db_database: str = module.params[u_skel.JsonTKN.DATABASE.value]
    db_username: str = module.params[u_skel.JsonTKN.USERNAME.value]
    db_password: str = module.params[u_skel.JsonTKN.PASSWORD.value]
    driver: Driver = u_cypher.get_neo4j_driver(
         db_instance_id=db_instance_id,
         db_username=db_username,
         db_password=db_password
    )
    cypher_query: str
    cypher_params: Dict[str, Any]
    cypher_query_inline: str
    cypher_query, cypher_params, cypher_query_inline = vertex(module.params)
    try:
        with driver.session(database=db_database) as session:
            response: Result = session.run(cypher_query, cypher_params)
    except Exception as e:
        module.fail_json(**u_skel.ansible_fail(diagnostics=f"{e}"))
    finally:
        driver.close()
    summary: ResultSummary = response.consume()
    payload: Dict[str, Any] = {
        u_skel.JsonTKN.CYPHER_QUERY.value: cypher_query,
        u_skel.JsonTKN.CYPHER_PARAMS.value: cypher_params,
        u_skel.JsonTKN.CYPHER_QUERY_INLINE.value: cypher_query_inline,
        u_skel.JsonTKN.STATS.value: u_cypher.cypher_stats(summary)
        }
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
