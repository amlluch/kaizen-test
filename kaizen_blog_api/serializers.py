import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple


def dict_factory(data: List[Tuple[str, Any]]) -> Dict[str, Any]:
    return {
        key: {
            dict_key: str(dict_value) if isinstance(dict_value, uuid.UUID) else dict_value
            for dict_key, dict_value in value.items()
        }
        if isinstance(value, Dict)
        else str(value)
        if isinstance(value, uuid.UUID)
        else value.timestamp()
        if isinstance(value, datetime)
        else value
        for key, value in data
        if value is not None
    }