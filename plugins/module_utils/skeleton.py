import os

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
    TYPE_DICT = "dict"
    TYPE_INT = "int"
    TYPE_STR = "str"

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
    FROM = "from"
    FROM_ENTITY_NAME = "from_entity_name"
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
    QUERY = "query"
    RELATIONSHIPS_CREATED = "relationships_created"
    RELATIONSHIPS_DELETED = "relationships_deleted"
    RESULT = "result"
    STATE = "state"
    STATS = "stats"
    TO = "to"
    TO_ENTITY_NAME = "to_entity_name"
    TYPE = "type"
    USERNAME = "username"
    QUERY_TYPE = "query_type"

def state_present(state: str) -> bool:
    return state.lower() == YamlState.PRESENT.value

def file_splitext(filename: str) -> str:
    return os.path.splitext(os.path.basename(filename))[0]

def ansible_fail(diagnostics) -> Dict[str, Any]:
    return { 
        JsonTKN.RESULT.value: False, 
        JsonTKN.CHANGED.value: False, 
        JsonTKN.MSG.value: diagnostics
        }

def ansible_exit(changed, payload_key, payload) -> Dict[str, Any]:
    return { 
        JsonTKN.RESULT.value: True,
        JsonTKN.CHANGED.value: changed,
        payload_key: payload
        }