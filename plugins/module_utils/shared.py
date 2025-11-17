"""
    Filename: ./module_utils/shared.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 4.1.0
    Description: 
        Shared utility functions
"""
from typing import Dict, Any, Tuple, List

import os
import yaml

from neo4j.time import DateTime, Date, Time

from . import skeleton as u_skel


import os
import yaml
from typing import Any, Dict, List, Tuple, Optional

def load_yaml_file(
    path: str
) -> Tuple[bool, Optional[List[Dict[str, Any]]], Dict[str, Any]]:

    # Check file existence
    if not os.path.exists(path):
        return False, None, {u_skel.JsonTKN.ERROR_MSG: f"Vertex file not found: {path}"}

    # Attempt load
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, None, {u_skel.JsonTKN.ERROR_MSG: f"Failed to parse YAML file: {e}"}
    except Exception as e:
        return False, None, {u_skel.JsonTKN.ERROR_MSG: f"Failed to read file: {e}"}

    # Validate top-level structure
    if not isinstance(payload, list):
        return False, None, {u_skel.JsonTKN.ERROR_MSG: "YAML must contain a list of vertex definitions"}

    # Success
    return True, payload, {}



def serialize_neo4j(
    value: Any
) -> Any:
    if isinstance(value, (DateTime, Date, Time)):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize_neo4j(v) for v in value]
    if isinstance(value, dict):
        return {k: serialize_neo4j(v) for k, v in value.items()}
    return value


def validate_vertex_file(
    vertices: List[Dict[str, Any]],
    vertex_spec: Dict[str, Dict[str, Any]]
) -> Tuple[bool, Dict[str, Any]]:
    for i, vertex in enumerate(vertices):
        for key, rules in vertex_spec.items():
            if rules.get(u_skel.YamlATTR.REQUIRED.value, False) and key not in vertex:
                return False, {u_skel.JsonTKN.ERROR_MSG: f"Vertex {i}: Missing required field '{key}'"}
            # Optional: type checks
            expected_type = rules.get(u_skel.YamlATTR.TYPE.value)
            if expected_type and key in vertex:
                if expected_type == u_skel.YamlATTR.TYPE_STR.value and not isinstance(vertex[key], str):
                    return False, {u_skel.JsonTKN.ERROR_MSG: f"Vertex {i}: Field '{key}' must be a string"}
    return True, {}
