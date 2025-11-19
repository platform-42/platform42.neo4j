echo "--- modules ---"
OBJECT="plugins/modules/graph_reset.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="plugins/modules/query.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="plugins/modules/vertex.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="plugins/modules/edge.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="plugins/modules/label.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="plugins/modules/constraint.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}



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
