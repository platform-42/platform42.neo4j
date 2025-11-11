from typing import Dict, Any, Callable, Tuple, List

from . import skeleton as u_skel
from . import schema as u_schema

def validate_cypher_inputs(
    module_params: Dict[str, Any],
    cypher_input_list: List
):
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
            validator(value)

def _validate_type(
    value: str
) -> Tuple[bool, Dict[str, Any]]:
    result, diagnostics = u_schema.validate_pattern(
        u_schema.SchemaProperties.TYPE,
        value
        )
    if not result:
        return False, diagnostics
    return True, {}
