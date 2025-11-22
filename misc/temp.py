BATCH_SIZE = 100

summary = u_stats.EntitySummary(total=len(vertices))

driver: Driver = u_driver.get_driver(module.params)

try:
    with driver.session(database=module.params[u_skel.JsonTKN.DATABASE.value]) as session:

        for batch_start in range(0, len(vertices), BATCH_SIZE):
            batch_vertices = vertices[batch_start : batch_start + BATCH_SIZE]

            batch_params: List[Dict[str, Any]] = []

            # prepare batch parameters and validate/cast each vertex
            for idx, vertex in enumerate(batch_vertices):
                result, validated_vertex, diagnostics = u_shared.validate_entity_from_file(
                    vertex, u_args.argument_spec_vertex()
                )
                if not result:
                    module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))

                input_list = [
                    u_skel.JsonTKN.LABEL.value,
                    u_skel.JsonTKN.ENTITY_NAME.value,
                    u_skel.JsonTKN.PROPERTIES.value
                ]
                result, casted_properties, diagnostics = u_input.validate_inputs(
                    cypher_input_list=input_list,
                    module_params=validated_vertex,
                    supports_unique_key=False,
                    supports_casting=True
                )
                if not result:
                    module.fail_json(**u_skel.ansible_fail(diagnostics=diagnostics))

                # merge vertex data and casted properties into batch param
                vertex_param = dict(validated_vertex)  # includes entity_name, label, etc.
                vertex_param.update(casted_properties)  # adds dynamic properties like row, column, domain, color
                batch_params.append(vertex_param)

            # generate UNWIND query using your templated MERGE/SET
            # we just replace direct params with 'v.' access inside UNWIND
            batch_query = f"""
            UNWIND $batch AS v
            MERGE (n:`Cell` {{entity_name: v.entity_name}})
            SET n += {{row: v.row, column: v.column, domain: v.domain, color: v.color}}
            """

            try:
                response: Result = session.run(batch_query, {"batch": batch_params})
                result_summary: ResultSummary = response.consume()
                summary.processed += len(batch_vertices)
                summary.nodes_created += result_summary.counters.nodes_created
                summary.nodes_deleted += result_summary.counters.nodes_deleted
                summary.labels_added += result_summary.counters.labels_added
                summary.labels_removed += result_summary.counters.labels_removed
                summary.properties_set += result_summary.counters.properties_set
            except Neo4jError as e:
                payload = u_skel.payload_fail(batch_query, {"batch": batch_params}, "UNWIND_BATCH", e, batch_start)
                module.fail_json(**u_skel.ansible_fail(diagnostics=payload))
            except Exception as e:  # pylint: disable=broad-exception-caught
                payload = u_skel.payload_abend("UNWIND_BATCH", e, batch_start)
                module.fail_json(**u_skel.ansible_fail(diagnostics=payload))

finally:
    driver.close()

nodes_changed: bool = (summary.nodes_created > 0 or summary.nodes_deleted > 0)
module.exit_json(**u_skel.ansible_exit(
    changed=nodes_changed,
    payload_key=module_name,
    payload=summary.as_payload()
))
