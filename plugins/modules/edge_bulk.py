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
        edge_from_file_result: Tuple[bool, Dict[str, Any], Dict[str, Any]] = u_shared.validate_vertex_from_file(
            edge, 
            u_args.argument_spec_edge()
            )
        result, validated_edge, diagnostics = edge_from_file_result
        if not result:
            module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))    

    nodes_changed: bool = (summary.created > 0 or summary.deleted > 0)
    module.exit_json(**u_skel.ansible_exit(
        changed=nodes_changed,
        payload_key=module_name,
        payload=validated_edge
        )
    )

if __name__ == '__main__':
    main()