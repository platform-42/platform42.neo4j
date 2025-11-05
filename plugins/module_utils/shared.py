# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,
# pylint: disable=line-too-long,too-many-arguments,too-many-locals
"""
    Filename: ./module_utils/shared.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 2.8.0
    Description: 
        Shared utility functions
"""
from typing import Dict, Any, Callable, Tuple
from datetime import datetime

import os
import re

from neo4j.time import DateTime, Date, Time
from . import skeleton as u_skel

def serialize_neo4j(
    value: Any
) -> Any:
    if isinstance(value, (DateTime, Date, Time)):
        return value.isoformat()
    elif isinstance(value, list):
        return [serialize_neo4j(v) for v in value]
    elif isinstance(value, dict):
        return {k: serialize_neo4j(v) for k, v in value.items()}
    else:
        return value

def parse_datetime(
    val: str
) -> datetime:
    return datetime.fromisoformat(val.replace("Z", "+00:00"))

def parse_bool(
    val: Any
) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes", "y")

def validate_optionals(
    properties: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
    casted_properties: Dict[str, Any]
    try:
        casted_properties = type_casted_properties(properties)
    except (KeyError, ValueError) as e:
        return False, {}, u_skel.ansible_diagnostics(e)
    except Exception as e:
        return False, {}, u_skel.ansible_diagnostics(e)
    return True, casted_properties, {}

# Mapping of type names to conversion functions
TYPE_HANDLERS: Dict[str, Callable[[Any], Any]] = {
    u_skel.YamlATTR.TYPE_INT.value: int,
    u_skel.YamlATTR.TYPE_FLOAT.value: float,
    u_skel.YamlATTR.TYPE_BOOL.value: parse_bool,
    u_skel.YamlATTR.TYPE_STR.value: str,
    u_skel.YamlATTR.TYPE_DATETIME.value: parse_datetime
}

#
#   type_casted_properties:
#   - a property now consists of a value and a type
#   - if the type is unknown, it is considered as a string
#     Cypher will emit an error if that assumption was wrong
#   - initial support for int, float, bool, datatime and str
#   - returns a new properties Dict with a casted value
#
def type_casted_properties(
    properties: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    casted_properties: Dict[str, Any] = {}
    for key, value in properties.items():
        # Ensure value is a dict
        if not isinstance(value, dict):
            raise ValueError(
                f"Property '{key}' must be a dict with 'value' and optional 'type', got {type(value).__name__}"
                )

        # Ensure 'value' exists
        if u_skel.JsonTKN.VALUE.value not in value:
            raise KeyError(
                f"Property '{key}' is missing required '{u_skel.JsonTKN.VALUE.value}' field"
                )

        raw_value = value[u_skel.JsonTKN.VALUE.value]
        data_type = value.get(u_skel.JsonTKN.TYPE.value, u_skel.YamlATTR.TYPE_STR.value)
        handler = TYPE_HANDLERS.get(data_type, str)

        try:
            casted_properties[key] = handler(raw_value)
        except Exception as e:
            raise ValueError(
                f"Failed to cast property '{key}' with value '{raw_value}' to type '{data_type}': {repr(e)}"
                )

    return casted_properties

def flatten_query(
    query: str
) -> str:
    return re.sub(r'\s+', ' ', query).strip()

def file_splitext(
    filename: str
) -> str:
    return os.path.splitext(os.path.basename(filename))[0]
