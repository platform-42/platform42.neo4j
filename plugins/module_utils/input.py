"""
    Filename: ./module_utils/input.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 4.1.0
    Description: 
        Validation of Cypher inputs acquired via YAML
"""
from typing import Dict, Any, Tuple, List, cast, Optional, Callable

from datetime import datetime

from . import skeleton as u_skel
from . import schema as u_schema

ValidationResult = Tuple[bool, Any]

#
#   validate_cypher_inputs:
#       check whether YAML tokens (valid JSON) are also valid NEO4J tokens
#       NEO4J implements additional contraints
#
def validate_cypher_inputs(
    cypher_input_list: List[str],
    module_params: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:

    mask = set(cypher_input_list)
    validated: Dict[str, Any] = {}

    VALIDATORS = { # pylint: disable=invalid-name
        u_skel.JsonTKN.TYPE.value: _validate_type,
        u_skel.JsonTKN.LABEL.value: _validate_label,
        u_skel.JsonTKN.BASE_LABEL.value: _validate_label,
        u_skel.JsonTKN.ENTITY_NAME.value: _validate_entity_name,
        u_skel.JsonTKN.FROM.value: _validate_from,
        u_skel.JsonTKN.TO.value: _validate_to,
        u_skel.JsonTKN.PROPERTIES.value: _validate_keys,
        u_skel.JsonTKN.PARAMETERS.value: _validate_keys,
        u_skel.JsonTKN.UNIQUE_KEY.value: _validate_key,
        u_skel.JsonTKN.PROPERTY_KEY.value: _validate_key,
    }

    for token in mask:
        validator = VALIDATORS.get(token)
        if not validator:
            continue

        value = module_params.get(token)
        if value is None:
            continue  # skip missing optional tokens

        result, response = validator(cast(Any, value))
        if not result:
            return False, response
        validated[token] = response

    return (True, validated)


def _validate_type(
    value: str
) -> ValidationResult:
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.NEO4J_IDENTIFIER, value)
    return (True, value) if result else (False, diagnostics)


def _validate_label(
    value: str
) -> ValidationResult:
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.NEO4J_IDENTIFIER, value)
    return (True, value) if result else (False, diagnostics)


def _validate_entity_name(
    value: str
) -> ValidationResult:
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.UNICODE_NAME, value)
    return (True, value) if result else (False, diagnostics)


def _validate_from(
    value: Dict[str, Any]
) -> ValidationResult:
    label = value.get(u_skel.JsonTKN.LABEL.value)
    if not label:
        return (False, {u_skel.JsonTKN.ERROR_MSG: "Missing FROM.LABEL"})
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.NEO4J_IDENTIFIER, label)
    if not result:
        return (False, diagnostics)

    entity = value.get(u_skel.JsonTKN.ENTITY_NAME.value)
    if not entity:
        return (False, {u_skel.JsonTKN.ERROR_MSG.value: "Missing FROM.ENTITY_NAME"})
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.UNICODE_NAME, entity)
    if not result:
        return (False, diagnostics)

    return (True, {u_skel.JsonTKN.LABEL.value: label, u_skel.JsonTKN.ENTITY_NAME.value: entity})


def _validate_to(
    value: Dict[str, Any]
) -> ValidationResult:
    label = value.get(u_skel.JsonTKN.LABEL.value)
    if not label:
        return (False, {u_skel.JsonTKN.ERROR_MSG.value: "Missing TO.LABEL"})
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.NEO4J_IDENTIFIER, label)
    if not result:
        return (False, diagnostics)

    entity = value.get(u_skel.JsonTKN.ENTITY_NAME.value)
    if not entity:
        return (False, {u_skel.JsonTKN.ERROR_MSG.value: "Missing TO.ENTITY_NAME"})
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.UNICODE_NAME, entity)
    if not result:
        return (False, diagnostics)

    return (True, {u_skel.JsonTKN.LABEL.value: label, u_skel.JsonTKN.ENTITY_NAME.value: entity})


def _validate_keys(
    value: Dict[str, Any]
) -> ValidationResult:
    validated = {}
    for key, val in value.items():
        result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.NEO4J_IDENTIFIER, key)
        if not result:
            return (False, diagnostics)
        validated[key] = val
    return (True, validated)


def _validate_key(
    value: str
) -> ValidationResult:
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.NEO4J_IDENTIFIER, value)
    return (True, value) if result else (False, diagnostics)

#
#   validate_unique_key:
#       a unique_key is a reference to an existing property key
#       so it mandates existence of properties and an instance of unique_key
#       as part of properies.keys()
#
def validate_unique_key(
    value: str,
    properties: Dict[str, Any]
) -> ValidationResult:
    if value is None:
        return (True, {})
    normalized_property_keys = [key.strip().lower() for key in properties.keys()]
    if value.strip().lower() not in normalized_property_keys:
        return (False, {u_skel.JsonTKN.ERROR_MSG.value: f"unique_key '{value}' not found in properties"})
    return (True, {})

#
#   validate_inputs:
#       overarching function to implements 3 functions
#       - validate_cypher_inputs -> valid NEO4J identifiers
#       - validate_unique_key -> integrity check with properties
#       - casted_properties -> typecasted properties
#
def validate_inputs(
    cypher_input_list: List[str],
    module_params: Dict[str, Any],
    supports_unique_key: Optional[bool] = False,
    supports_casting: Optional[bool] = False,
) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:

    # validate vertex/edge properties type, label, base_label and entity_name
    # validate properties and parameter keys
    result, diagnostics = validate_cypher_inputs(
        cypher_input_list,
        module_params
        )
    if not result:
        return (False, {}, diagnostics)

    # validate whether unique_key value is a valid property
    if supports_unique_key:
        result, diagnostics = validate_unique_key(
            module_params[u_skel.JsonTKN.UNIQUE_KEY.value],
            module_params[u_skel.JsonTKN.PROPERTIES.value]
        )
        if not result:
            return (False, {}, diagnostics)

    # cast (dynamic) properties and (dynamic) parameters via type/value definition
    casted_values: Dict[str, Any] = {}
    if supports_casting:
        if u_skel.JsonTKN.PROPERTIES.value in module_params:
            result, casted_values, diagnostics = type_casted_properties(
                module_params[u_skel.JsonTKN.PROPERTIES.value]
                )
            if not result:
                return (False, {}, diagnostics)
        if u_skel.JsonTKN.PARAMETERS.value in module_params:
            result, casted_values, diagnostics = type_casted_properties(
                module_params[u_skel.JsonTKN.PARAMETERS.value]
                )
            if not result:
                return (False, {}, diagnostics)
    return (True, casted_values, {})

#
#   typecasting for properties
#
def type_casted_properties(
    properties: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
    result, casted_properties, diagnostics = type_casting(properties)
    if not result:
        return (False, {}, diagnostics)
    return (True, casted_properties, {})


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
        return (False, [], {
            u_skel.JsonTKN.ERROR_MSG.value:
                f"Expected list for 'list' type, got {type(element_value).__name__}"
        })

    handler = TYPE_HANDLERS.get(element_type)
    if handler is None:
        return (False, [], {
            u_skel.JsonTKN.ERROR_MSG.value:
                f"Unsupported element type for list: {element_type}"
        })

    try:
        return (True, [handler(v) for v in element_value], {})
    except Exception as e: # pylint: disable=broad-exception-caught
        return (False, [], {
            u_skel.JsonTKN.ERROR_MSG.value:
                f"Failed to cast list elements to '{element_type}': {repr(e)}"
        })


def type_casting(
    properties: Dict[str, Dict[str, Any]]
) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
    casted_properties: Dict[str, Any] = {}

    for key, prop in properties.items():
        if not isinstance(prop, dict):
            return (False, {}, {
                u_skel.JsonTKN.ERROR_MSG.value:
                    f"Property '{key}' must be a dict with 'value' and optional 'type', "
                    f"got {type(prop).__name__}"
            })

        if u_skel.JsonTKN.VALUE.value not in prop:
            return (False, {}, {
                u_skel.JsonTKN.ERROR_MSG.value:
                    f"Property '{key}' is missing required '{u_skel.JsonTKN.VALUE.value}' field"
            })

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
                return (False, {}, diag)
            casted_properties[key] = casted_list
        else:
            handler = TYPE_HANDLERS.get(data_type, str)
            try:
                casted_value = handler(raw_value)
                casted_properties[key] = casted_value
            except Exception as e: # pylint: disable=broad-exception-caught
                return (False, {}, {
                    u_skel.JsonTKN.ERROR_MSG.value:
                        f"Failed to cast property '{key}' with value '{raw_value}' "
                        f"to type '{data_type}': {repr(e)}"
                })

    return (True, casted_properties, {})
