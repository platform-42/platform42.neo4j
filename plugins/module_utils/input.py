"""
    Filename: ./module_utils/input.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 4.0.0
    Description: 
        Validation of Cypher inputs acquired via YAML
"""
from typing import Dict, Any, Tuple, List, cast

from . import skeleton as u_skel
from . import schema as u_schema

ValidationResult = Tuple[bool, Any]

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

    return True, validated


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
        return False, {u_skel.JsonTKN.ERROR_MSG: "Missing FROM.LABEL"}
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.NEO4J_IDENTIFIER, label)
    if not result:
        return False, diagnostics

    entity = value.get(u_skel.JsonTKN.ENTITY_NAME.value)
    if not entity:
        return False, {u_skel.JsonTKN.ERROR_MSG: "Missing FROM.ENTITY_NAME"}
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.UNICODE_NAME, entity)
    if not result:
        return False, diagnostics

    return True, {u_skel.JsonTKN.LABEL.value: label, u_skel.JsonTKN.ENTITY_NAME.value: entity}


def _validate_to(
    value: Dict[str, Any]
) -> ValidationResult:
    label = value.get(u_skel.JsonTKN.LABEL.value)
    if not label:
        return False, {u_skel.JsonTKN.ERROR_MSG: "Missing TO.LABEL"}
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.NEO4J_IDENTIFIER, label)
    if not result:
        return False, diagnostics

    entity = value.get(u_skel.JsonTKN.ENTITY_NAME.value)
    if not entity:
        return False, {u_skel.JsonTKN.ERROR_MSG: "Missing TO.ENTITY_NAME"}
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.UNICODE_NAME, entity)
    if not result:
        return False, diagnostics

    return True, {u_skel.JsonTKN.LABEL.value: label, u_skel.JsonTKN.ENTITY_NAME.value: entity}


def _validate_keys(
    value: Dict[str, Any]
) -> ValidationResult:
    validated = {}
    for key, val in value.items():
        result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.NEO4J_IDENTIFIER, key)
        if not result:
            return False, diagnostics
        validated[key] = val
    return True, validated


def _validate_key(
    value: str
) -> ValidationResult:
    result, diagnostics = u_schema.validate_patterns(u_schema.IdentifierPattern.NEO4J_IDENTIFIER, value)
    return (True, value) if result else (False, diagnostics)


def validate_unique_key(
    value: str,
    properties: Dict[str, Any]
) -> ValidationResult:
    normalized_property_keys = [key.strip().lower() for key in properties.keys()]
    if value.strip().lower() not in normalized_property_keys:
        return False, {u_skel.JsonTKN.ERROR_MSG: f"unique_key '{value}' not found in properties"}    
    return True, {}
