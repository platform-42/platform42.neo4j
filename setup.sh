#!/usr/bin/env bash
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
VENV_DIR=${SCRIPTPATH}/venv

if [ ! -d ${VENV_DIR} ]; then
    python3 -m venv ${VENV_DIR}
fi

cd ${SCRIPTPATH}

source ${VENV_DIR}/bin/activate
pip install --upgrade pip
pip install ansible

