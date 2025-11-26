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
---
module: edge
short_description: Create or update a relationship (edge) between two vertices in Neo4j via bulk load
version_added: "4.2.0"
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
  - bulk interface expects all relationship attributes in a YAML inputfile
'''

EXAMPLES = r'''
#
# Only attributes of a NEO4J edge are moved edge YAML-file
# u1_tracks: is the edge_anchor (start marker) in the edge YAML-file
#
# u1_tracks:
# - properties:
#     distance:
#       value: 1.2
#       type: float
#   from:
#     entity_name: "Kurfürstenstraße"
#     label: Station
#   to:
#     entity_name: "Hallerstraße"
#     label: Station
#   type: Track
#   bi_directional: True
#
- name: "create edges via input YAML"
  platform42.neo4j.edge_bulk:
    neo4j_uri: "neo4j://127.0.0.1:7687"
    database: "neo4j"
    username: "neo4j"
    password: "*****"
    edge_file: "./vars/edges/u1_tracks.yml"
    edge_anchor: "u1_tracks"
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
            check_mode=check_mode,
            is_bulk=True,
            relation_type=relation_type,
            label_from=label_from,
            entity_name_from=entity_name_from,
            label_to=label_to,
            entity_name_to=entity_name_to,
            properties=properties,
            bi_directional=bi_directional,
            unique_key=unique_key
        )
    return u_cypher.edge_del(
        check_mode=check_mode,
        relation_type=relation_type,
        label_from=label_from,
        entity_name_from=entity_name_from,
        label_to=label_to,
        entity_name_to=entity_name_to,
        bi_directional=bi_directional,
        unique_key=unique_key
    )


def main() -> None:
    module_name: str = u_skel.file_splitext(__file__)
    module: AnsibleModule = AnsibleModule(
        argument_spec=u_args.argument_spec_neo4j() | u_args.argument_spec_edge_bulk(),
        supports_check_mode=True
        )

    # load edges from YAML-file
    edge_load_result: Tuple[bool, List[Dict[str, Any]], Dict[str, Any]] = u_shared.load_yaml_file(
        module.params[u_skel.JsonTKN.EDGE_FILE.value],
        module.params[u_skel.JsonTKN.EDGE_ANCHOR.value]
        )
    result, edges, diagnostics = edge_load_result
    if not result:
        module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))

    batch_size: int = 100
    edge_results: List[Tuple[str, Dict[str, Any], str]] = []
    summary = u_stats.EntitySummary(total=len(edges))
    driver: Driver = u_driver.get_driver(module.params)
    for _, edge in enumerate(edges):

        # check YAML-edge for completeness
        edge_from_file_result: Tuple[bool, Dict[str, Any], Dict[str, Any]] = u_shared.validate_entity_from_file(
            edge,
            u_args.argument_spec_edge()
            )
        result, validated_edge, diagnostics = edge_from_file_result
        if not result:
            module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))

        # validate YAML against NEO4J constraints, typecast dynamic properties
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

        # generate cypher query for edge operation (create/delete)
        edge_result: Tuple[str, Dict[str, Any], str] = edge_module(
            module.check_mode,
            validated_edge,
            casted_properties
            )

        # save cypher_query, cypher_params in edge_results
        edge_results.append(edge_result)

    # bundle edges in groups of batch_size - convert query to bulk paradigm
    edge_bulk: List[Tuple[str, Dict[str, Any]]] = u_cypher.edge_bulk_add(
        edge_results,
        batch_size
    )
    try:
        # execute cypher query
        with driver.session(database=module.params[u_skel.JsonTKN.DATABASE.value]) as session:

            # iterate over bulk-queries
            for edge_bulk_query, edge_bulk_params in edge_bulk:
                try:
                    response: Result = session.run(edge_bulk_query, edge_bulk_params)
                    result_summary: ResultSummary = response.consume()
                    summary.processed += len(edge_bulk_params[u_skel.JsonTKN.BATCH.value])
                    summary.relationships_created += result_summary.counters.relationships_created
                    summary.relationships_deleted += result_summary.counters.relationships_deleted
                    summary.properties_set += result_summary.counters.properties_set
                except Neo4jError as e:
                    payload = u_skel.payload_fail(
                        cypher_query=edge_bulk_query,
                        cypher_params=edge_bulk_params[u_skel.JsonTKN.BATCH.value],
                        e=e,
                        idx=summary.processed
                        )
                    module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
                except Exception as e: # pylint: disable=broad-exception-caught
                    payload = u_skel.payload_abend(e)
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
