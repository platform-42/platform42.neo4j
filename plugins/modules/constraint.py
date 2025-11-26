#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Filename: ./modules/constraint.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-27
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


def constraint_module(
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


def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_neo4j() | u_args.argument_spec_constraint(),
        supports_check_mode=True
        )
    input_list: List[str] = [
        u_skel.JsonTKN.LABEL.value,
        u_skel.JsonTKN.PROPERTY_KEY.value
        ]
    validate_result: Tuple[bool, Dict[str, Any], Dict[str, Any]] = u_input.validate_inputs(
        cypher_input_list=input_list,
        module_params=module.params,
        supports_unique_key=False,
        supports_casting=False
        )
    result, _, diagnostics = validate_result
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
    driver: Driver = u_driver.get_driver(module.params)
    constraint_result: Tuple[str, Dict[str, Any], str] = constraint_module(
        module.check_mode,
        module.params
        )
    cypher_query, cypher_params, cypher_query_inline = constraint_result
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
    state: str = module.params[u_skel.JsonTKN.STATE.value]
    counters: SummaryCounters = result_summary.counters
    constraints_changed: int = counters.constraints_added if u_skel.state_present(state) else counters.constraints_removed
    changed: bool = constraints_changed > 0
    module.exit_json(**u_skel.ansible_exit(
        changed=changed,
        payload_key=module_name,
        payload=payload)
        )


if __name__ == '__main__':
    main()
