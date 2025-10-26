# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
"""
    Filename: ./module_utils/shared.py
    Author: diederick de Buck (diederick.de.buck@gmail.com)
    Date: 2025-10-26
    Version: 1.6.0
    Description: 
        Shared utility functions
"""
import os
import re

def flatten_query(
    query: str
) -> str:
    return re.sub(r'\s+', ' ', query).strip()

def file_splitext(
    filename: str
) -> str:
    return os.path.splitext(os.path.basename(filename))[0]
