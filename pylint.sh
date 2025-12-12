#!/usr/bin/env bash
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
VENV_DIR=${SCRIPTPATH}/venv

source ${VENV_DIR}/bin/activate
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
OBJECT="plugins/modules/edge_bulk.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="plugins/modules/vertex_bulk.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}

PYTHONPATH=./plugins/module_utils
cd ${PYTHONPATH}

echo "--- module_utils ---"
OBJECT="argument_spec.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="cypher_query.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="cypher.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="driver"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="input.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="schema.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="shared.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="skeleton.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}
OBJECT="stats.py"
echo "linting ${OBJECT}"; pylint ${OBJECT}


