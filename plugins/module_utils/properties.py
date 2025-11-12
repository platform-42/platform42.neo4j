"""
    Filename: ./module_utils/properties.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 3.2.0
    Description: 
        Shared utility functions
"""

from typing import Dict, Any, Callable, Tuple, List
from datetime import datetime

from . import skeleton as u_skel


def type_casted_properties(
    properties: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
    success, casted, diagnostics = type_casting(properties)
    if not success:
        return False, {}, diagnostics
    return True, casted, {}


def parse_datetime(val: str) -> datetime:
    return datetime.fromisoformat(val.replace("Z", "+00:00"))


def parse_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes", "y")


TYPE_HANDLERS: Dict[str, Callable[[Any], Any]] = {
    u_skel.YamlATTR.TYPE_INT.value: int,
    u_skel.YamlATTR.TYPE_FLOAT.value: float,
    u_skel.YamlATTR.TYPE_BOOL.value: parse_bool,
    u_skel.YamlATTR.TYPE_STR.value: str,
    u_skel.YamlATTR.TYPE_DATETIME.value: parse_datetime,
}


def parse_list(
    element_value: Any,
    element_type: str
) -> Tuple[bool, List[Any], Dict[str, Any]]:
    if not isinstance(element_value, list):
        return False, [], {
            u_skel.JsonTKN.ERROR_MSG.value:
                f"Expected list for 'list' type, got {type(element_value).__name__}"
        }

    handler = TYPE_HANDLERS.get(element_type)
    if handler is None:
        return False, [], {
            u_skel.JsonTKN.ERROR_MSG.value:
                f"Unsupported element type for list: {element_type}"
        }

    try:
        return True, [handler(v) for v in element_value], {}
    except Exception as e:
        return False, [], {
            u_skel.JsonTKN.ERROR_MSG.value:
                f"Failed to cast list elements to '{element_type}': {repr(e)}"
        }


def type_casting(
    properties: Dict[str, Dict[str, Any]]
) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
    casted_properties: Dict[str, Any] = {}

    for key, prop in properties.items():
        if not isinstance(prop, dict):
            return False, {}, {
                u_skel.JsonTKN.ERROR_MSG.value:
                    f"Property '{key}' must be a dict with 'value' and optional 'type', "
                    f"got {type(prop).__name__}"
            }

        if u_skel.JsonTKN.VALUE.value not in prop:
            return False, {}, {
                u_skel.JsonTKN.ERROR_MSG.value:
                    f"Property '{key}' is missing required '{u_skel.JsonTKN.VALUE.value}' field"
            }

        raw_value = prop[u_skel.JsonTKN.VALUE.value]
        data_type = prop.get(u_skel.JsonTKN.TYPE.value, u_skel.YamlATTR.TYPE_STR.value)

        # Handle list types explicitly
        if data_type == u_skel.YamlATTR.TYPE_LIST.value:
            element_type = prop.get(
                u_skel.JsonTKN.ELEMENT_TYPE.value,
                u_skel.YamlATTR.TYPE_STR.value
            )
            result, casted_list, diag = parse_list(raw_value, element_type)
            if not result:
                return False, {}, diag
            casted_properties[key] = casted_list
        else:
            handler = TYPE_HANDLERS.get(data_type, str)
            try:
                casted_value = handler(raw_value)
                casted_properties[key] = casted_value
            except Exception as e:
                return False, {}, {
                    u_skel.JsonTKN.ERROR_MSG.value:
                        f"Failed to cast property '{key}' with value '{raw_value}' "
                        f"to type '{data_type}': {repr(e)}"
                }

    return True, casted_properties, {}
