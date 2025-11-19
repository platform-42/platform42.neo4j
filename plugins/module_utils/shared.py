"""
    Filename: ./module_utils/shared.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 4.1.0
    Description: 
        Shared utility functions
"""
from typing import Dict, Any, Tuple, List, Optional

import os
import yaml

from neo4j.time import DateTime, Date, Time

from . import skeleton as u_skel


def load_yaml_file(
    vertex_path: str,
    vertex_anchor: str,
) -> Tuple[bool, Optional[List[Dict[str, Any]]], Dict[str, Any]]:

    # check file existence
    if not os.path.exists(vertex_path):
        return False, None, {u_skel.JsonTKN.ERROR_MSG.value: f"YAML file not found: {vertex_path}"}

    # load yaml into payload
    try:
        with open(vertex_path, "r", encoding="utf-8") as f:
            extract = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, None, {u_skel.JsonTKN.ERROR_MSG.value: f"Failed to parse YAML file: {e}"}
    except Exception as e:
        return False, None, {u_skel.JsonTKN.ERROR_MSG.value: f"Failed to read fYAML file: {e}"}

    # examine structure of payload
    if not isinstance(extract, dict):
        return False, None, {u_skel.JsonTKN.ERROR_MSG.value: "YAML must have one top-level key"}

    keys = list(extract.keys())

    # must have 1 top key
    if len(keys) != 1:
        return False, None, {u_skel.JsonTKN.ERROR_MSG.value: f"YAML must have top-level key named '{vertex_anchor}'"}

    anchor = keys[0]
    # anchor must match exactly
    if anchor != vertex_anchor:
        return False, None, {u_skel.JsonTKN.ERROR_MSG.value: f"Top-level key '{anchor}' does not match '{vertex_anchor}'"}

    payload = extract[anchor]

    # --- List validation ------------------------------------------------------
    if not isinstance(payload, list):
        return False, None, {u_skel.JsonTKN.ERROR_MSG.value: f"Top-level key '{anchor}' must contain a list"}

    # --- Success --------------------------------------------------------------
    diagnostics: Dict[str, Any] = {
        u_skel.JsonTKN.VERTEX_ANCHOR.value: anchor,
        u_skel.JsonTKN.COUNT.value: len(payload)
    }
    return (True, payload, diagnostics)


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


def validate_vertex_from_file(
    vertex: Dict[str, Any],
    vertex_spec: Dict[str, Dict[str, Any]]
) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:

    validated = {}
    for key, rules in vertex_spec.items():
        is_required = rules.get(u_skel.YamlATTR.REQUIRED.value, False)
        default_val = rules.get(u_skel.YamlATTR.DEFAULT.value, None)
        expected_type = rules.get(u_skel.YamlATTR.TYPE.value)

        # Required field missing
        if is_required and key not in vertex:
            return (
                False,
                {},
                {u_skel.JsonTKN.ERROR_MSG.value: f"Missing required field '{key}'"}
            )

        # Value chosen: from vertex or from default
        validated[key] =  vertex[key] if key in vertex else default_val

        # Type checking (only when value is present)
        if expected_type and validated[key] is not None:
            if expected_type == u_skel.YamlATTR.TYPE_STR.value and not isinstance(validated[key], str):
                return (
                    False,
                    {},
                    {u_skel.JsonTKN.ERROR_MSG.value: f"Field '{key}' must be a string"}
                )

    return (True, validated, {})
