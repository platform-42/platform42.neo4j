# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,
"""
    Filename: ./module_utils/argument_spec.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 4.1.0
    Description: 
        Ansible module argument spec
"""
from typing import Dict, Any

from . import skeleton as u_skel


def argument_spec_neo4j() -> Dict[str, Any]:
    return {
        u_skel.JsonTKN.NEO4J_URI.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.DATABASE.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.USERNAME.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.PASSWORD.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True,
            u_skel.YamlATTR.NO_LOG.value: True
        }
    }


def argument_spec_graph_reset() -> Dict[str, Any]:
    return {}


def argument_spec_constraint() -> Dict[str, Any]:
    return {
        u_skel.JsonTKN.LABEL.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.STATE.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: u_skel.YamlState.PRESENT.value
        },
        u_skel.JsonTKN.PROPERTY_KEY.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        }
    }

def argument_spec_query() -> Dict[str, Any]:
    return {
        u_skel.JsonTKN.QUERY.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.PARAMETERS.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_DICT.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: {}
        },
        u_skel.JsonTKN.WRITE_ACCESS.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_BOOL.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: False
        }
    }


def argument_spec_vertex() -> Dict[str, Any]:
    return {
        u_skel.JsonTKN.LABEL.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.ENTITY_NAME.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.PROPERTIES.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_DICT.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: {}
        },
        u_skel.JsonTKN.STATE.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: u_skel.YamlState.PRESENT.value
        },
        u_skel.JsonTKN.SINGLETON.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_BOOL.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: True
        }
    }

def argument_spec_vertex_bulk() -> Dict[str, Any]:
    return {
        u_skel.JsonTKN.VERTEX_FILE.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.VERTEX_ANCHOR.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        }
    }

def argument_spec_edge() -> Dict[str, Any]:
    return {
        u_skel.JsonTKN.TYPE.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.FROM.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_DICT.value,
            u_skel.YamlATTR.REQUIRED.value: True,
            u_skel.YamlATTR.OPTION.value: {
                u_skel.JsonTKN.LABEL.value: {
                    u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
                    u_skel.YamlATTR.REQUIRED.value: True
                },
                u_skel.JsonTKN.ENTITY_NAME.value: {
                    u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
                    u_skel.YamlATTR.REQUIRED.value: True
                },
            },
        },
        u_skel.JsonTKN.TO.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_DICT.value,
            u_skel.YamlATTR.REQUIRED.value: True,
            u_skel.YamlATTR.OPTION.value: {
                u_skel.JsonTKN.LABEL.value: {
                    u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
                    u_skel.YamlATTR.REQUIRED.value: True
                },
                u_skel.JsonTKN.ENTITY_NAME.value: {
                    u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
                    u_skel.YamlATTR.REQUIRED.value: True
                },
            },
        },
        u_skel.JsonTKN.PROPERTIES.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_DICT.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: {}
        },
        u_skel.JsonTKN.BI_DIRECTIONAL.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_BOOL.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: False
        },
        u_skel.JsonTKN.STATE.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: u_skel.YamlState.PRESENT.value
        },
        u_skel.JsonTKN.UNIQUE_KEY.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: None
        }
    }


def argument_spec_label() -> Dict[str, Any]:
    return {
        u_skel.JsonTKN.BASE_LABEL.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.LABEL.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.ENTITY_NAME.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.STATE.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: u_skel.YamlState.PRESENT.value
        }
    }
