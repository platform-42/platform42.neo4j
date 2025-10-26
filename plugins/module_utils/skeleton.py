# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
"""
    Filename: ./module_utils/skeleton.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 1.6.0
    Description: 
        Ansible core skeleton functions
"""
from typing import Dict, Any, Callable, Dict
from strenum import StrEnum

class YamlATTR(StrEnum):
    CHANGED = "changed"
    DEFAULT = "default"
    MSG = "msg"
    NO_LOG = "no_log"
    OPTION = "option"
    REQUIRED = "required"
    RESULT = "result"
    TYPE = "type"
    TYPE_BOOL = "bool"
    TYPE_DICT = "dict"
    TYPE_INT = "int"
    TYPE_STR = "str"
    TYPE_FLOAT = "float"

class YamlState(StrEnum):
    ABSENT = "absent"
    PRESENT = "present"

class JsonTKN(StrEnum):
    BI_DIRECTIONAL = "bi_directional"
    CHANGED = "changed"
    CYPHER_PARAMS = "cypher_params"
    CYPHER_QUERY = "cypher_query"
    CYPHER_QUERY_INLINE = "cypher_query_inline"
    CYPHER_RESPONSE = "cypher_response"
    DATA = "data"
    DATABASE = "database"
    DIAGNOSTICS = "diagnostics"
    ENTITY_NAME = "entity_name"
    ENTITY_NAME_FROM = "entity_name_from"
    ENTITY_NAME_TO = "entity_name_to"
    ERROR_MSG = "error_msg"
    FROM = "from"
    JSON_KEYS = "json_keys"
    LABEL = "label"
    LABELS = "labels"
    LABELS_ADDED = "labels_added"
    LABELS_REMOVED = "labels_removed"
    MSG = "msg"
    NEO4J_URI = "neo4j_uri"
    NODE_ID = "node_id"
    NODES_CREATED = "nodes_created"
    NODES_DELETED = "nodes_deleted"
    PARAMETERS = "parameters"
    PASSWORD = "password"
    PATTERN = "pattern"
    PROPERTIES = "properties"
    PROPERTIES_SET = "properties_set"
    QUERY = "query"
    QUERY_TYPE = "query_type"
    RELATIONSHIPS_CREATED = "relationships_created"
    RELATIONSHIPS_DELETED = "relationships_deleted"
    RESULT = "result"
    STATE = "state"
    STATS = "stats"
    TO = "to"
    TYPE = "type"
    USERNAME = "username"
    VALUE = "value"

def state_present(
    state: str
) -> bool:
    return state.lower() == str(YamlState.PRESENT.value)

def parse_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes", "y")

# Mapping of type names to conversion functions
TYPE_HANDLERS: Dict[str, Callable[[Any], Any]] = {
    YamlATTR.TYPE_INT.value: int,
    YamlATTR.TYPE_FLOAT: float,
    YamlATTR.TYPE_BOOL: parse_bool,
    YamlATTR.TYPE_STR: str
}

#
#   ansible_cast_properties
#       a little bit of voodo
#       - remember, a property now consists of a value and a type
#       - if the type is unknown, it is considered as a string
#       - Cypher will emit an error if that assumption was wrong
#       - initial support for int, float, bool and str
#       - we simply return a new properties Dict with a casted value
#
def type_casted_properties(
    properties: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    return {
        key: TYPE_HANDLERS.get(
            value.get(JsonTKN.TYPE.value, YamlATTR.TYPE_STR.value), str)(value[JsonTKN.VALUE.value])
        for key, value in properties.items()
    }


def ansible_fail(
    diagnostics: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        JsonTKN.RESULT.value: False,
        JsonTKN.CHANGED.value: False,
        JsonTKN.MSG.value: diagnostics
        }

def ansible_exit(
    changed: bool,
    payload_key: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        JsonTKN.RESULT.value: True,
        JsonTKN.CHANGED.value: changed,
        payload_key: payload
        }
