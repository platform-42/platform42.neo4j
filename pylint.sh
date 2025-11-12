
pylint plugins/modules/graph_reset.py
pylint plugins/modules/query_read.py
pylint plugins/modules/vertex.py
pylint plugins/modules/edge.py

PYTHONPATH=./plugins/module_utils
PYLINT_INIT_HOOK=--init-hook "import sys; sys.path.append('./plugins')

cd $PYTHONPATH
pylint --init-hook "import sys; sys.path.append('./plugins')" argument_spec.py
pylint --init-hook "import sys; sys.path.append('./plugins')" cypher_query.py
pylint --init-hook "import sys; sys.path.append('./plugins')" cypher.py
pylint --init-hook "import sys; sys.path.append('./plugins')" driver
pylint --init-hook "import sys; sys.path.append('./plugins')" input.py
pylint --init-hook "import sys; sys.path.append('./plugins')" properties.py
pylint --init-hook "import sys; sys.path.append('./plugins')" schema.py
pylint --init-hook "import sys; sys.path.append('./plugins')" shared.py
pylint --init-hook "import sys; sys.path.append('./plugins')" skeleton.py
