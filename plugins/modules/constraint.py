#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,
# pylint: disable=line-too-long,too-many-arguments,too-many-locals
"""
    Filename: ./modules/constraint.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-27
    Version: 2.8.0
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

from neo4j import Driver, ResultSummary, Result
from neo4j.exceptions import Neo4jError

DOCUMENTATION = r'''
---
module: ./plugins/modules/constraint.py
short_description: Manage uniqueness constraints in Neo4j
version_added: "2.3.0"
description:
  - This module ensures the presence or absence of a uniqueness constraint
    on a given label and property (key) within a Neo4j database.
  - Constraints are used to guarantee that a property value is unique
    for all nodes of a given label, preventing accidental duplication.
  - The module is idempotent and safe to run multiple times.
  - It uses the Neo4j C( CREATE CONSTRAINT IF NOT EXISTS ) and C( DROP CONSTRAINT IF EXISTS )
    Cypher statements under the hood.
author:
  - Diederick de Buck (diederick.de.buck@gmail.com)
'''

EXAMPLES = r'''
- name: "Ensure uniqueness constraint for User.entity_name"
  platform42.neo4j.constraint:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    label: User
    property_key: entity_name
    state: PRESENT

- name: "Remove uniqueness constraint from Account.account_id"
  platform42.neo4j.constraint:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    label: Account
    property_key: account_id
    state: ABSENT
'''

def constraint(
    check_mode: bool,
    module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:
    state: str = module_params[u_skel.JsonTKN.STATE.value]
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    property_key: str = module_params[u_skel.JsonTKN.PROPERTY_KEY.value]
    if u_skel.state_present(state):
        return u_cypher.constraint_add(
            check_mode=check_mode,
            label=label,
            property_key=property_key
            )
    return u_cypher.constraint_del(
        check_mode=check_mode,
        label=label,
        property_key=property_key
        )

def validate_cypher_inputs(
    module_params: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    result: bool
    diagnostics: Dict[str, Any]
    # validate label against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.LABEL,
        module_params[u_skel.JsonTKN.LABEL.value]
        )
    if not result:
        return False, diagnostics
    # validate property_key against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.PROPERTY_KEY,
        module_params[u_skel.JsonTKN.PROPERTY_KEY.value]
        )
    if not result:
        return False, diagnostics
    return True, {}

def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_constraint(),
        supports_check_mode=True
    )
    result, diagnostics = validate_cypher_inputs(module.params)
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    driver: Driver = u_driver.get_driver(module.params)
    cypher_query: str
    cypher_params: Dict[str, Any]
    cypher_query_inline: str
    cypher_query, cypher_params, cypher_query_inline = constraint(
        module.check_mode,
        module.params
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
    constraints_changed: int = summary.counters.constraints_added if u_skel.state_present(state) else summary.counters.constraints_removed
    changed: bool = constraints_changed > 0
    module.exit_json(**u_skel.ansible_exit(
        changed=changed,
        payload_key=module_name,
        payload=payload)
    )

if __name__ == '__main__':
    main()
