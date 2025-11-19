#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Filename: ./modules/edge_bulk.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-05
    Version: 4.2.0
    Description: 
        Ansible module to create graph relationships (edge) as a bulk
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

from neo4j import Driver, ResultSummary, Result
from neo4j.exceptions import Neo4jError

DOCUMENTATION = r'''
'''

EXAMPLES = r'''
'''

def edge_module(
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


def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_neo4j() | u_args.argument_spec_edge_bulk(),
        supports_check_mode=True
        )
    edge_load_result: Tuple[bool, List[Dict[str, Any]], Dict[str, Any]] = u_shared.load_yaml_file(
        module.params[u_skel.JsonTKN.EDGE_FILE.value],
        module.params[u_skel.JsonTKN.EDGE_ANCHOR.value]
        )
    result, edges, diagnostics = edge_load_result
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))

    summary = u_stats.EdgeSummary(total=len(edges))
    for idx, edge in enumerate(edges):
        edge_from_file_result: Tuple[bool, Dict[str, Any], Dict[str, Any]] = u_shared.validate_model_from_file(
            edge, 
            u_args.argument_spec_edge()
            )
        result, validated_edge, diagnostics = edge_from_file_result
        if not result:
            module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))    
        input_list: List[str] = [
            u_skel.JsonTKN.TYPE.value,
            u_skel.JsonTKN.FROM.value,
            u_skel.JsonTKN.TO.value,
            u_skel.JsonTKN.PROPERTIES.value,
            u_skel.JsonTKN.UNIQUE_KEY.value
            ]
        validate_result: Tuple[bool, Dict[str, Any], Dict[str, Any]] = u_input.validate_inputs(
            cypher_input_list=input_list,
            module_params=validated_edge,
            supports_unique_key=False,
            supports_casting=True
            )
        result, casted_properties, diagnostics = validate_result
        if not result:
            module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
        edge_result: Tuple[str, Dict[str, Any], str] = edge_module(
            module.check_mode,
            validated_edge,
            casted_properties
            )
        cypher_query, cypher_params, cypher_query_inline = edge_result
        driver: Driver = u_driver.get_driver(module.params)
        try:
            with driver.session(database=module.params[u_skel.JsonTKN.DATABASE.value]) as session:
                response: Result = session.run(cypher_query, cypher_params)
                cypher_response: List[Dict[str, Any]] = [record.data() for record in list(response)]
                result_summary: ResultSummary = response.consume()
            summary.processed += 1
            summary.relationships_created += result_summary.counters.relationships_created
            summary.relationships_deleted += result_summary.counters.relationships_deleted                
        except Neo4jError as e:
            payload = u_skel.payload_fail(cypher_query, cypher_params, cypher_query_inline, e)
            module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
        except Exception as e: # pylint: disable=broad-exception-caught
            payload = u_skel.payload_abend(cypher_query_inline, e)
            module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
        finally:
            driver.close()
    nodes_changed: bool = (summary.relationships_created > 0 or summary.relationships_deleted > 0)
    module.exit_json(**u_skel.ansible_exit(
        changed=nodes_changed,
        payload_key=module_name,
        payload=summary.as_payload()
        )
    )

if __name__ == '__main__':
    main()