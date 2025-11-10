"""
    Filename: ./module_utils/skeleton.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 3.1.0
    Description: 
        Ansible core skeleton functions
"""
import os
import re

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
    TYPE_LIST = "list"
    TYPE_STR = "str"

class YamlState(StrEnum):
    ABSENT = "absent"
    PRESENT = "present"

class JsonTKN(StrEnum):
    ARGS = "args"
    BASE_LABEL = "base_label"
    BI_DIRECTIONAL = "bi_directional"
    CHANGED = "changed"
    CONSTRAINTS_ADDED = "constraints_added"
    CONSTRAINTS_REMOVED = "constraints_removed"
    CYPHER_PARAMS = "cypher_params"
    CYPHER_QUERY = "cypher_query"
    CYPHER_QUERY_INLINE = "cypher_query_inline"
    CYPHER_RESPONSE = "cypher_response"
    DATABASE = "database"
    DIAGNOSTICS = "diagnostics"
    ELEMENT_TYPE = "element_type"
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
    MODULE = "module"
    MSG = "msg"
    NEO4J_URI = "neo4j_uri"
    NODES_CREATED = "nodes_created"
    NODES_DELETED = "nodes_deleted"
    PARAMETERS = "parameters"
    PASSWORD = "password"
    PATTERN = "pattern"
    PROPERTIES = "properties"
    PROPERTIES_SET = "properties_set"
    PROPERTY_KEY = "property_key"
    QUERY = "query"
    QUERY_TYPE = "query_type"
    RELATIONSHIPS_CREATED = "relationships_created"
    RELATIONSHIPS_DELETED = "relationships_deleted"
    REPR = "repr"
    RESULT = "result"
    SINGLETON = "singleton"
    STATE = "state"
    STATS = "stats"
    TO = "to"
    TYPE = "type"
    UNIQUE_KEY = "unique_key"
    USERNAME = "username"
    VALUE = "value"
    WRITE_ACCESS = "write_access"
    VERTEX_FILE = "vertex_file"

def state_present(
    state: str
) -> bool:
    return state.lower() == str(YamlState.PRESENT.value)

def flatten_query(
    query: str
) -> str:
    return re.sub(r'\s+', ' ', query).strip()

def file_splitext(
    filename: str
) -> str:
    return os.path.splitext(os.path.basename(filename))[0]

def payload_exit(
    cypher_query: str,
    cypher_params: Dict[str, Any],
    cypher_query_inline: str,
    cypher_response: Any,
    stats: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        JsonTKN.CYPHER_QUERY.value: flatten_query(cypher_query),
        JsonTKN.CYPHER_PARAMS.value: cypher_params,
        JsonTKN.CYPHER_QUERY_INLINE.value: flatten_query(cypher_query_inline),
        JsonTKN.STATS.value: stats,
        JsonTKN.CYPHER_RESPONSE.value: cypher_response
        }

# catastrophic failure - cypher buffers might be corrupted
def payload_abend(
    cypher_query_inline: str,
    e: BaseException
) -> Dict[str, Any]:
    return {
        JsonTKN.RESULT.value: "abend - failure due to system exception",
        JsonTKN.CYPHER_QUERY_INLINE.value: cypher_query_inline,
        JsonTKN.DIAGNOSTICS.value: ansible_diagnostics(e)
        }

# functional failure - cypher buffers have consistent state
def payload_fail(
    cypher_query: str,
    cypher_params: Dict[str, Any],
    cypher_query_inline: str,
    e: BaseException
) -> Dict[str, Any]:
    return {
        JsonTKN.CYPHER_QUERY.value: flatten_query(cypher_query),
        JsonTKN.CYPHER_PARAMS.value: cypher_params,
        JsonTKN.CYPHER_QUERY_INLINE.value: flatten_query(cypher_query_inline),
        JsonTKN.DIAGNOSTICS.value: ansible_diagnostics(e)
        }

def ansible_diagnostics(
    e: BaseException
) -> Dict[str, Any]:
    return {
        JsonTKN.TYPE.value: type(e).__name__,
        JsonTKN.MODULE.value: type(e).__module__,
        JsonTKN.ERROR_MSG.value: str(e),
        JsonTKN.REPR.value: repr(e),
        JsonTKN.ARGS.value: list(e.args)
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
