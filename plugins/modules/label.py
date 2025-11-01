#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,line-too-long
"""
    Filename: ./modules/label.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-27
    Version: 2.7.0
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

from neo4j import Driver, ResultSummary, Result

DOCUMENTATION = r'''
---
module: label
short_description: Manage labels on existing Neo4j nodes
version_added: "2.5.0"
description:
  - Add or remove labels on existing Neo4j nodes.
  - Supports idempotent operations using Cypher C(SET n:`Label`) and C(REMOVE n:`Label`)
    to modify node classifications dynamically without duplicating or losing data.
  - Useful for managing node states, categories, or roles declaratively in Neo4j.
author:
  - Diederick de Buck (diederick.de.buck@gmail.com)
'''

EXAMPLES = r'''
- name: "Add label Verified to user entity_name=Alice"
  platform42.neo4j.label:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    base_label: User
    entity_name: Alice
    label: Verified
    state: PRESENT

- name: "Remove label Verified to user entity_name=Alice"
  platform42.neo4j.label:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    base_label: User
    entity_name: Alice
    label: Verified
    state: ABSENT
'''

def label(
    check_mode: bool,
    module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:
    base_label: str = module_params[u_skel.JsonTKN.BASE_LABEL.value]
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    entity_name: str = module_params[u_skel.JsonTKN.ENTITY_NAME.value]
    state: str = module_params[u_skel.JsonTKN.STATE.value]
    if u_skel.state_present(state):
        return u_cypher.label_add(
            check_mode=check_mode,
            base_label=base_label,
            label=label,
            entity_name=entity_name
            )
    return u_cypher.label_del(
        check_mode=check_mode,
        base_label=base_label,
        label=label,
        entity_name=entity_name
        )

def validate_cypher_inputs(
    module_params: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    result: bool
    diagnostics: Dict[str, Any]
    # validate base_label against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.LABEL,
        module_params[u_skel.JsonTKN.BASE_LABEL.value]
        )
    if not result:
        return False, diagnostics
    # validate label against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.LABEL,
        module_params[u_skel.JsonTKN.LABEL.value]
        )
    if not result:
        return False, diagnostics
    # validate entity_name against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.ENTITY_NAME,
        module_params[u_skel.JsonTKN.ENTITY_NAME.value]
        )
    if not result:
        return False, diagnostics
    return True, {}

def main() -> None:
    module_name: str = u_shared.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_label(),
        supports_check_mode=True
    )
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
    cypher_query, cypher_params, cypher_query_inline = label(
        module.check_mode,
        module.params
    )
    payload: Dict[str, Any]
    try:
        with driver.session(database=db_database) as session:
            response: Result = session.run(cypher_query, cypher_params)
            records = list(response)
            cypher_response: List[Dict[str, Any]] = [record.data() for record in records]
            summary: ResultSummary = response.consume()
    except Exception as e:
        payload = {
            u_skel.JsonTKN.CYPHER_QUERY.value: u_shared.flatten_query(cypher_query),
            u_skel.JsonTKN.CYPHER_PARAMS.value: cypher_params,
            u_skel.JsonTKN.CYPHER_QUERY_INLINE.value: u_shared.flatten_query(cypher_query_inline),
            u_skel.JsonTKN.ERROR_MSG.value: u_skel.ansible_diagnostics(e)
        }
        module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
    finally:
        driver.close()
    payload: Dict[str, Any] = {
        u_skel.JsonTKN.CYPHER_QUERY.value: u_shared.flatten_query(cypher_query),
        u_skel.JsonTKN.CYPHER_PARAMS.value: cypher_params,
        u_skel.JsonTKN.CYPHER_QUERY_INLINE.value: u_shared.flatten_query(cypher_query_inline),
        u_skel.JsonTKN.STATS.value: u_cypher.cypher_stats(summary),
        u_skel.JsonTKN.CYPHER_RESPONSE.value: u_shared.serialize_neo4j(cypher_response)
        }
    state: str = module.params[u_skel.JsonTKN.STATE.value]
    constraints_changed: int = summary.counters.constraints_added if u_skel.state_present(state) else summary.counters.constraints_removed
    changed: bool = constraints_changed > 0
    module.exit_json(**u_skel.ansible_exit(
        changed=changed,
        payload_key=module_name,
        payload=payload)
    )

if __name__ == '__main__':
    main()
