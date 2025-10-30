#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,line-too-long
"""
    Filename: ./modules/constraint.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-27
    Version: 2.6.0
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
module: ./plugins/modules/constraint.py
short_description: Manage uniqueness constraints in Neo4j
version_added: "2.3.0"
description:
  - This module ensures the presence or absence of a uniqueness constraint
    on a given label and property within a Neo4j database.
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
    property: entity_name
    state: PRESENT

- name: "Remove uniqueness constraint from Account.account_id"
  platform42.neo4j.constraint:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    label: Account
    property: account_id
    state: ABSENT
'''

def constraint(
    check_mode: bool,
    module_params: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:
    state: str = module_params[u_skel.JsonTKN.STATE.value]
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    property: str = module_params[u_skel.JsonTKN.PROPERTY.value]
    if u_skel.state_present(state):
        return u_cypher.constraint_add(
            check_mode=check_mode,
            label=label,
            property=property
            )
    return u_cypher.constraint_del(
        check_mode=check_mode,
        label=label,
        property=property
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
    # validate property against injection
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.PROPERTY,
        module_params[u_skel.JsonTKN.PROPERTY.value]
        )
    if not result:
        return False, diagnostics
    return True, {}

def main() -> None:
    module_name: str = u_shared.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_constraint(),
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
    cypher_query, cypher_params, cypher_query_inline = constraint(
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
        diagnostics = {
            u_skel.JsonTKN.CYPHER_QUERY.value: u_shared.flatten_query(cypher_query),
            u_skel.JsonTKN.CYPHER_PARAMS.value: cypher_params,
            u_skel.JsonTKN.CYPHER_QUERY_INLINE.value: u_shared.flatten_query(cypher_query_inline),
            u_skel.JsonTKN.ERROR_MSG.value: repr(e)
        }
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
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
