
pylint plugins/modules/graph_reset.py
pylint plugins/modules/query.py
pylint plugins/modules/vertex.py
pylint plugins/modules/edge.py
pylint plugins/modules/label.py
pylint plugins/modules/constraint.py


PYTHONPATH=./plugins/module_utils

cd ${PYTHONPATH}
pylint argument_spec.py
pylint cypher_query.py
pylint cypher.py
pylint driver
pylint input.py
pylint schema.py
pylint shared.py
pylint skeleton.py
