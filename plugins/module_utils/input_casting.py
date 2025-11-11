"""
    Filename: ./module_utils/shared.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 3.1.0
    Description: 
        Shared utility functions
"""
from typing import Dict, Any, Callable, Tuple, List
from datetime import datetime

from . import skeleton as u_skel



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

# Mapping of type names to conversion functions
TYPE_HANDLERS: Dict[str, Callable[[Any], Any]] = {
    u_skel.YamlATTR.TYPE_INT.value: int,
    u_skel.YamlATTR.TYPE_FLOAT.value: float,
    u_skel.YamlATTR.TYPE_BOOL.value: parse_bool,
    u_skel.YamlATTR.TYPE_STR.value: str,
    u_skel.YamlATTR.TYPE_DATETIME.value: parse_datetime
}

def parse_list(
    element_value: Any,
    element_type: str
) -> List[Any]:
    if not isinstance(element_value, list):
        raise TypeError(
            f"Expected a list for type 'list', got {type(element_value).__name__}"
            )

    # Reuse your existing handlers for element types
    handler = TYPE_HANDLERS.get(element_type)
    if handler is None:
        raise ValueError(
            f"Unsupported element type for list: {element_type}"
            )

    try:
        return [handler(v) for v in element_value]
    except Exception as e:
        raise ValueError(
            f"Failed to cast list elements to '{element_type}': {repr(e)}"
            )

#
#   type_casted_properties:
#   - a property now consists of value and type for simple types.
#   - a property now consists of value, type and element_type for list of simple type.
#   - if the type is unknown, it is considered as a string.
#       Cypher will emit an error if that assumption was wrong.
#   - initial support for int, float, bool, datatime, str and list.
#   - returns a new properties Dict with a casted value.
#
def type_casted_properties(
    properties: Dict[str, Dict[str, Any]]
) -> Tuple[bool, Dict[str, Any]]:
    casted_properties: Dict[str, Any] = {}

    for key, value in properties.items():
        # Validate structure
        if not isinstance(value, dict):
            error_msg = f"Property '{key}' must be a dict with 'value' and optional 'type', got {type(value).__name__}"
            return False, {u_skel.JsonTKN.ERROR_MSG.value: error_msg}

        if u_skel.JsonTKN.VALUE.value not in value:
            error_msg = f"Property '{key}' is missing required '{u_skel.JsonTKN.VALUE.value}' field"
            return False, {u_skel.JsonTKN.ERROR_MSG.value: error_msg}

        raw_value = value[u_skel.JsonTKN.VALUE.value]
        data_type = value.get(u_skel.JsonTKN.TYPE.value, u_skel.YamlATTR.TYPE_STR.value)

        # Handle list types explicitly
        if data_type == u_skel.YamlATTR.TYPE_LIST.value:
            element_type = value.get(
                u_skel.JsonTKN.ELEMENT_TYPE.value,
                u_skel.YamlATTR.TYPE_STR.value
            )
            casted_value = parse_list(raw_value, element_type)
        else:
            handler = TYPE_HANDLERS.get(data_type, str)
            try:
                casted_value = handler(raw_value)
            except Exception as e:
                raise ValueError(
                    f"Failed to cast property '{key}' with value '{raw_value}' to type '{data_type}': {repr(e)}"
                )
        # Assign final casted value
        casted_properties[key] = casted_value

    return True, casted_properties
