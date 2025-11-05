# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,
# pylint: disable=line-too-long,too-many-arguments
"""
    Filename: ./module_utils/schema.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 2.8.0
    Description: 
        Ansible schema validation - originates from JSON-schema validation,
        morphed into regex-based validation
"""
from typing import Dict, Any, Tuple
from enum import Enum
from strenum import StrEnum

import regex

from . import skeleton as u_skel

class IdentifierPattern(StrEnum):
    UNICODE_NAME = r"^[\p{L}\p{N}_\s\-\(\)]*$"
    NEO4J_IDENTIFIER = r"^[A-Za-z_][A-Za-z0-9_]*$"

class SchemaProperties(Enum):
    LABEL = {
        u_skel.JsonTKN.TYPE.value: "string",
        u_skel.JsonTKN.PATTERN.value: IdentifierPattern.NEO4J_IDENTIFIER.value
        }
    TYPE = {
        u_skel.JsonTKN.TYPE.value: "string",
        u_skel.JsonTKN.PATTERN.value: IdentifierPattern.NEO4J_IDENTIFIER.value
        }
    ENTITY_NAME = {
        u_skel.JsonTKN.TYPE.value: "string",
        u_skel.JsonTKN.PATTERN.value: IdentifierPattern.UNICODE_NAME.value
        }
    PROPERTY_KEY = {
        u_skel.JsonTKN.TYPE.value: "string",
        u_skel.JsonTKN.PATTERN.value: IdentifierPattern.NEO4J_IDENTIFIER.value
        }
    PROPERTY_KEYS = {
        u_skel.JsonTKN.TYPE.value: "string",
        u_skel.JsonTKN.PATTERN.value: IdentifierPattern.NEO4J_IDENTIFIER.value
        }

def validate_pattern(
    schema_property: SchemaProperties,
    value: str
) -> Tuple[bool, Dict[str, Any]]:
    pattern: IdentifierPattern = schema_property.value[u_skel.JsonTKN.PATTERN.value]
    if not regex.match(pattern, value):
        return False, {u_skel.JsonTKN.ERROR_MSG.value: f"value {value} must match pattern {pattern}"}
    return True, {}
