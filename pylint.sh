
pylint plugins/modules/graph_reset.py
pylint plugins/modules/query_read.py
pylint plugins/modules/vertex.py
pylint plugins/modules/edge.py

PYTHONPATH=./plugins/module_utils 
pylint argument_spec.py
pylint cypher_query.py
pylint schema.py
pylint skeleton.py
