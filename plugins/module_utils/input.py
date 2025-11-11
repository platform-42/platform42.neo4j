from typing import Dict, Any, Callable, Tuple, List

from . import skeleton as u_skel
from . import schema as u_schema

def validate_cypher_inputs(
    cypher_input_list: List[str],
    module_params: Dict[str, Any]
) -> None:
    mask = set(cypher_input_list)

    VALIDATORS = {
        u_skel.JsonTKN.TYPE.value: _validate_type,
    }

    for token in mask:
        validator = VALIDATORS.get(token)
        if not validator:
            continue  # Ignore tokens not handled here
        value = module_params.get(token)
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
