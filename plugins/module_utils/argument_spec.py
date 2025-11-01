# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,line-too-long
"""
    Filename: ./module_utils/argument_spec.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 2.6.0
    Description: 
        Ansible module argument spec
"""
from typing import Dict, Any

from . import skeleton as u_skel

def argument_spec_graph_reset() -> Dict[str, Any]:
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
            u_skel.YamlATTR.REQUIRED.value: True
        }
    }

def argument_spec_constraint() -> Dict[str, Any]:
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
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.LABEL.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.STATE.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: u_skel.YamlState.PRESENT.value
        },
        u_skel.JsonTKN.PROPERTY.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        }
    }

def argument_spec_query_read() -> Dict[str, Any]:
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
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.QUERY.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_STR.value,
            u_skel.YamlATTR.REQUIRED.value: True
        },
        u_skel.JsonTKN.PARAMETERS.value: {
            u_skel.YamlATTR.TYPE.value: u_skel.YamlATTR.TYPE_DICT.value,
            u_skel.YamlATTR.REQUIRED.value: False,
            u_skel.YamlATTR.DEFAULT.value: {}
        }
    }

def argument_spec_vertice() -> Dict[str, Any]:
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

def argument_spec_edge() -> Dict[str, Any]:
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
            u_skel.YamlATTR.REQUIRED.value: True
        },
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
            u_skel.YamlATTR.REQUIRED.value: True
        },
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