from typing import Dict, Any, Callable, Tuple, List

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
        u_skel.JsonTKN.FROM.value: _validate_from,
        u_skel.JsonTKN.TO.value: _validate_to,
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
    result, diagnostics = u_schema.validate_pattern_2(
        u_schema.IdentifierPattern.NEO4J_IDENTIFIER,
        value
        )
    if not result:
        return False, diagnostics
    return True, {}

def _validate_label(
    value: str
) -> Tuple[bool, Dict[str, Any]]:
    result, diagnostics = u_schema.validate_pattern_2(
        u_schema.IdentifierPattern.NEO4J_IDENTIFIER,
        value
        )
    if not result:
        return False, diagnostics
    return True, {}

def _validate_from(
    value: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    result, diagnostics = u_schema.validate_pattern_2(
        u_schema.IdentifierPattern.NEO4J_IDENTIFIER,
        value[u_skel.JsonTKN.LABEL.value]
        )
    if not result:
        return False, diagnostics
    result, diagnostics = u_schema.validate_pattern_2(
        u_schema.IdentifierPattern.UNICODE_NAME,
        value[u_skel.JsonTKN.ENTITY_NAME.value]
        )
    if not result:
        return False, diagnostics
    return True, {}

def _validate_to(
    value: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    result, diagnostics = u_schema.validate_pattern_2(
        u_schema.IdentifierPattern.NEO4J_IDENTIFIER,
        value[u_skel.JsonTKN.LABEL.value]
        )
    if not result:
        return False, diagnostics
    result, diagnostics = u_schema.validate_pattern_2(
        u_schema.IdentifierPattern.UNICODE_NAME,
        value[u_skel.JsonTKN.ENTITY_NAME.value]
        )
    if not result:
        return False, diagnostics
    return True, {}