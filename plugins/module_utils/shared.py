# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
"""
    Filename: ./module_utils/shared.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 2.0.0
    Description: 
        Shared utility functions
"""
from typing import Dict, Any, Callable, Tuple

import os
import re

from . import skeleton as u_skel

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
        return False, {}, { u_skel.JsonTKN.ERROR_MSG.value: repr(e) }
    except Exception as e:
        return False, {}, { u_skel.JsonTKN.ERROR_MSG.value: repr(e) }
    return True, casted_properties, {}

# Mapping of type names to conversion functions
TYPE_HANDLERS: Dict[str, Callable[[Any], Any]] = {
    u_skel.YamlATTR.TYPE_INT.value: int,
    u_skel.YamlATTR.TYPE_FLOAT.value: float,
    u_skel.YamlATTR.TYPE_BOOL.value: parse_bool,
    u_skel.YamlATTR.TYPE_STR.value: str
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
    casted_properties: Dict[str, Any] = {}
    for key, value in properties.items():
        # Ensure value is a dict
        if not isinstance(value, dict):
            raise ValueError(
                f"Property '{key}' must be a dict with 'value' and optional 'type', got {type(value).__name__}"
            )

        # Ensure 'value' exists
        if u_skel.JsonTKN.VALUE.value not in value:
            raise KeyError(f"Property '{key}' is missing required '{u_skel.JsonTKN.VALUE.value}' field")

        raw_val = value[u_skel.JsonTKN.VALUE.value]
        data_type = value.get(u_skel.JsonTKN.TYPE.value, u_skel.YamlATTR.TYPE_STR.value)
        handler = TYPE_HANDLERS.get(data_type, str)

        try:
            casted_properties[key] = handler(raw_val)
        except Exception as e:
            raise ValueError(
                f"Failed to cast property '{key}' with value '{raw_val}' to type '{data_type}': {e}"
            )

    return casted_properties

def type_casted_properties_2(
    properties: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    casted_properties: Dict[str, Any] = {}
    for key, value in properties.items():
        try:
            raw_value = value[u_skel.JsonTKN.VALUE.value]
        except KeyError:
            raise KeyError(
                f"Property '{key}' missing '{u_skel.JsonTKN.VALUE.value}' field")

        data_type = value.get(
            u_skel.JsonTKN.TYPE.value, 
            u_skel.YamlATTR.TYPE_STR.value
            )
        handler = TYPE_HANDLERS.get(data_type, str)
        try:
            casted_properties[key] = handler(raw_value)
        except Exception as e:
            raise ValueError(
                f"Failed to cast property '{key}' with value '{raw_value}' to type '{data_type}': {e}"
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
