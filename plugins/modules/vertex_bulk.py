#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Filename: ./modules/vertex_bulk.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-05
    Version: 4.1.0
    Description: 
        Ansible module to create graph nodes (vertex) as a bulk
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
#
# Only attributes of a NEO4J vertex are moved vertex YAML-file
# u1_stations: is the vertex_anchor (start marker) in the vertex YAML-file
# 
# u1_stations:
# - label: "Station"
#   state: PRESENT
#   entity_name: "Krumme Lanke"
#   singleton: True
#
- name: "create vertices via input YAML"
  platform42.neo4j.vertex_bulk:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    vertex_file: "./vars/vertices/u1_stations.yml"
    vertex_anchor: "u1_stations"
'''

def vertex_module(
    check_mode: bool,
    module_params: Dict[str, Any],
    properties: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:
    label: str = module_params[u_skel.JsonTKN.LABEL.value]
    entity_name: str = module_params[u_skel.JsonTKN.ENTITY_NAME.value]
    state: str = module_params[u_skel.JsonTKN.STATE.value]
    singleton: bool = module_params[u_skel.JsonTKN.SINGLETON.value]
    if u_skel.state_present(state):
        return u_cypher.vertex_add(
            check_mode=check_mode,
            is_bulk=True,
            singleton=singleton,
            label=label,
            entity_name=entity_name,
            properties=properties
            )
    return u_cypher.vertex_del(
        check_mode=check_mode,
        label=label,
        entity_name=entity_name
        )


def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_neo4j() | u_args.argument_spec_vertex_bulk(),
        supports_check_mode=True
        )
    
    # load vertices from YAML-file
    vertex_load_result: Tuple[bool, List[Dict[str, Any]], Dict[str, Any]] = u_shared.load_yaml_file(
        module.params[u_skel.JsonTKN.VERTEX_FILE.value],
        module.params[u_skel.JsonTKN.VERTEX_ANCHOR.value]
        )
    result, vertices, diagnostics = vertex_load_result
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))

    summary = u_stats.EntitySummary(total=len(vertices))
    for idx, vertex in enumerate(vertices):
        # check YAML-vertex for completeness
        vertex_from_file_result: Tuple[bool, Dict[str, Any], Dict[str, Any]] = u_shared.validate_entity_from_file(
            vertex,
            u_args.argument_spec_vertex()
            )
        result, validated_vertex, diagnostics = vertex_from_file_result
        if not result:
            module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
        # validate YAML against NEO4J constraints, typecast dynamic properties
        input_list: List[str] = [
            u_skel.JsonTKN.LABEL.value,
            u_skel.JsonTKN.ENTITY_NAME.value,
            u_skel.JsonTKN.PROPERTIES.value
            ]
        validate_result: Tuple[bool, Dict[str, Any], Dict[str, Any]] = u_input.validate_inputs(
            cypher_input_list=input_list,
            module_params=validated_vertex,
            supports_unique_key=False,
            supports_casting=True
            )
        result, casted_properties, diagnostics = validate_result
        if not result:
            module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))
        # generate cypher query for vertex operation (create/delete)
        vertex_result: Tuple[str, Dict[str, Any], str] = vertex_module(
            module.check_mode,
            validated_vertex,
            casted_properties
            )
        cypher_query, cypher_params, cypher_query_inline = vertex_result
        driver: Driver = u_driver.get_driver(module.params)
        try:
            # execute cypher query
            with driver.session(database=module.params[u_skel.JsonTKN.DATABASE.value]) as session:
                response: Result = session.run(cypher_query, cypher_params)
#               cypher_response: List[Dict[str, Any]] = [record.data() for record in list(response)]
                result_summary: ResultSummary = response.consume()
            summary.processed += 1
            summary.nodes_created += result_summary.counters.nodes_created
            summary.nodes_deleted += result_summary.counters.nodes_deleted
            summary.labels_added += result_summary.counters.labels_added
            summary.labels_removed += result_summary.counters.labels_removed
            summary.properties_set += result_summary.counters.properties_set
        except Neo4jError as e:
            payload = u_skel.payload_fail(cypher_query, cypher_params, cypher_query_inline, e, idx)
            module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
        except Exception as e: # pylint: disable=broad-exception-caught
            payload = u_skel.payload_abend(cypher_query_inline, e, idx)
            module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
        finally:
            driver.close()
    nodes_changed: bool = (summary.nodes_created > 0 or summary.nodes_deleted > 0)
    module.exit_json(**u_skel.ansible_exit(
        changed=nodes_changed,
        payload_key=module_name,
        payload=summary.as_payload()
        )
    )


if __name__ == '__main__':
    main()
