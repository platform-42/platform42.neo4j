"""
    Filename: ./module_utils/shared.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 3.1.0
    Description: 
        Shared utility functions
"""
from typing import Dict, Any, Tuple, List

import os
import yaml

from neo4j.time import DateTime, Date, Time

from . import skeleton as u_skel


def load_yaml_file(
    path: str
) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Vertex file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file {path}: {e}")

    if not isinstance(data, list):
        raise ValueError(f"Vertex file {path} must contain a list of vertex definitions")

    return data


def serialize_neo4j(
    value: Any
) -> Any:
    if isinstance(value, (DateTime, Date, Time)):
        return value.isoformat()
    elif isinstance(value, list):
        return [serialize_neo4j(v) for v in value]
    elif isinstance(value, dict):
        return {k: serialize_neo4j(v) for k, v in value.items()}
    else:
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
