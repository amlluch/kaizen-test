import json
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Tuple

from marshmallow import fields


def dict_factory(data: List[Tuple[str, Any]]) -> Dict[str, Any]:
    return {
        key: {
            dict_key: str(dict_value) if isinstance(dict_value, uuid.UUID) else dict_value
            for dict_key, dict_value in value.items()
        }
        if isinstance(value, Dict)
        else str(value)
        if isinstance(value, uuid.UUID)
        else Decimal(value.timestamp())
        if isinstance(value, datetime)
        else value
        for key, value in data
        if value is not None
    }


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        return json.JSONEncoder.default(self, o)


class CustomDateTimeField(fields.DateTime):
    """Accept datetime values that are already datetime type"""

    def _deserialize(self, value, attr, data, **kwargs):  # type: ignore
        if isinstance(value, Decimal):
            value = datetime.fromtimestamp(int(value))
        if isinstance(value, datetime):
            return value
        return super()._deserialize(value, attr, data)


class CustomDateField(fields.Date):
    """Accept date values that are already date type"""

    def _deserialize(self, value, attr, data, **kwargs):  # type: ignore
        if isinstance(value, date):
            return value
        return super()._deserialize(value, attr, data)
