"""
    Filename: ./module_utils/input.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 3.1.0
    Description: 
        Validation of Cypher inputs acquired via YAML
"""
from typing import Dict, Any, Tuple, List

from . import skeleton as u_skel
from . import schema as u_schema

def validate_cypher_inputs(
    cypher_input_list: List[str],
    module_params: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    mask = set(cypher_input_list)

    VALIDATORS = {
        u_skel.JsonTKN.TYPE.value: _validate_type,
        u_skel.JsonTKN.LABEL.value: _validate_label,
        u_skel.JsonTKN.BASE_LABEL.value: _validate_label,
        u_skel.JsonTKN.ENTITY_NAME.value: _validate_entity_name,
        u_skel.JsonTKN.FROM.value: _validate_from,
        u_skel.JsonTKN.TO.value: _validate_to,
        u_skel.JsonTKN.PROPERTIES.value: _validate_keys,
        u_skel.JsonTKN.PARAMETERS.value: _validate_keys,
        u_skel.JsonTKN.UNIQUE_KEY.value: _validate_key,
        u_skel.JsonTKN.PROPERTY_KEY.value: _validate_key
    }

    for token in mask:
        validator = VALIDATORS.get(token)
        if not validator:
            continue  # Ignore tokens not handled here
        value: Any = module_params.get(token)
        if value is not None:
            result, diagnostics = validator(value)
        if not result:
            return False, diagnostics
    return True, {}

def _validate_type(
    value: str
) -> Tuple[bool, Dict[str, Any]]:
    result, diagnostics = u_schema.validate_pattern(
        u_schema.IdentifierPattern.NEO4J_IDENTIFIER,
        value
        )
    if not result:
        return False, diagnostics
    return True, {}

def _validate_label(
    value: str
) -> Tuple[bool, Dict[str, Any]]:
    result, diagnostics = u_schema.validate_pattern(
        u_schema.IdentifierPattern.NEO4J_IDENTIFIER,
        value
        )
    if not result:
        return False, diagnostics
    return True, {}

def _validate_entity_name(
    value: str
) -> Tuple[bool, Dict[str, Any]]:
    result, diagnostics = u_schema.validate_pattern(
        u_schema.IdentifierPattern.UNICODE_NAME,
        value
        )
    if not result:
        return False, diagnostics
    return True, {}

def _validate_from(
    value: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    result, diagnostics = u_schema.validate_pattern(
        u_schema.IdentifierPattern.NEO4J_IDENTIFIER,
        value[u_skel.JsonTKN.LABEL.value]
        )
    if not result:
        return False, diagnostics
    result, diagnostics = u_schema.validate_pattern(
        u_schema.IdentifierPattern.UNICODE_NAME,
        value[u_skel.JsonTKN.ENTITY_NAME.value]
        )
    if not result:
        return False, diagnostics
    return True, {}

def _validate_to(
    value: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    result, diagnostics = u_schema.validate_pattern(
        u_schema.IdentifierPattern.NEO4J_IDENTIFIER,
        value[u_skel.JsonTKN.LABEL.value]
        )
    if not result:
        return False, diagnostics
    result, diagnostics = u_schema.validate_pattern(
        u_schema.IdentifierPattern.UNICODE_NAME,
        value[u_skel.JsonTKN.ENTITY_NAME.value]
        )
    if not result:
        return False, diagnostics
    return True, {}

def _validate_keys(
    value: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    for key in value.keys():
        result, diagnostics = u_schema.validate_pattern(
            u_schema.IdentifierPattern.NEO4J_IDENTIFIER,
            key
        )
        if not result:
            return False, diagnostics
    return True, {}

def _validate_key(
    value: str
) -> Tuple[bool, Dict[str, Any]]:
    result, diagnostics = u_schema.validate_pattern(
        u_schema.IdentifierPattern.NEO4J_IDENTIFIER,
        value
        )
    if not result:
        return False, diagnostics
    return True, {}