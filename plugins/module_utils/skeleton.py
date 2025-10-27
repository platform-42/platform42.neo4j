# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,line-too-long
"""
    Filename: ./module_utils/skeleton.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 2.3.0
    Description: 
        Ansible core skeleton functions
"""
from typing import Dict, Any
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
    TYPE_DATETIME = "datetime"
    TYPE_DICT = "dict"
    TYPE_FLOAT = "float"
    TYPE_INT = "int"
    TYPE_STR = "str"

class YamlState(StrEnum):
    ABSENT = "absent"
    PRESENT = "present"

class JsonTKN(StrEnum):
    BI_DIRECTIONAL = "bi_directional"
    CHANGED = "changed"
    CONSTRAINTS_ADDED = "constraints_added"
    CONSTRAINTS_REMOVED = "constraints_removed"
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
    PROPERTY = "property"
    QUERY = "query"
    QUERY_TYPE = "query_type"
    RELATIONSHIPS_CREATED = "relationships_created"
    RELATIONSHIPS_DELETED = "relationships_deleted"
    RESULT = "result"
    STATE = "state"
    STATS = "stats"
    TO = "to"
    TYPE = "type"
    UNIQUE = "unique"
    USERNAME = "username"
    VALUE = "value"

def state_present(
    state: str
) -> bool:
    return state.lower() == str(YamlState.PRESENT.value)

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
