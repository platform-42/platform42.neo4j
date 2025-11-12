
pylint plugins/modules/graph_reset.py
pylint plugins/modules/query_read.py
pylint plugins/modules/vertex.py
pylint plugins/modules/edge.py

PYTHONPATH=./plugins/module_utils
PYLINT_INIT_HOOK="--init-hook "import sys; sys.path.append('./plugins')"

cd $PYTHONPATH
pylint ${PYLINT_INIT_HOOK} argument_spec.py
pylint ${PYLINT_INIT_HOOK} cypher_query.py
pylint ${PYLINT_INIT_HOOK} cypher.py
pylint ${PYLINT_INIT_HOOK} driver
pylint ${PYLINT_INIT_HOOK} input.py
pylint ${PYLINT_INIT_HOOK} properties.py
pylint ${PYLINT_INIT_HOOK} schema.py
pylint ${PYLINT_INIT_HOOK} shared.py
pylint ${PYLINT_INIT_HOOK} skeleton.py
