"""
    Filename: ./module_utils/schema.py
    Author: diederick de Buck (diederick.de.buck@platform-42.com)
    Date: 2025-10-26
    Version: 4.3.0
    Description: 
        Ansible schema validation - originates from JSON-schema validation,
        morphed into regex-based validation
"""
from typing import Dict, Any, Tuple
from strenum import StrEnum

import regex

from . import skeleton as u_skel


class IdentifierPattern(StrEnum):
    UNICODE_NAME = r"^[\p{L}\p{N}_\s\-\(\)]*$"
    NEO4J_IDENTIFIER = r"^[A-Za-z_][A-Za-z0-9_]*$"


def validate_patterns(
    pattern: IdentifierPattern,
    value: str
) -> Tuple[bool, Dict[str, Any]]:
    if not regex.match(pattern.value, value):
        return (False, {u_skel.JsonTKN.ERROR_MSG.value: f"value {value} must match pattern {pattern}"})
    return (True, {})
