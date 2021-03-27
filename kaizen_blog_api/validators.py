from datetime import date, datetime
from typing import Any, Dict, Type, TypeVar, cast

from marshmallow import Schema, exceptions
from marshmallow_dataclass import class_schema

from kaizen_blog_api.errors import ValidationError
from kaizen_blog_api.serializers import CustomDateField, CustomDateTimeField

T = TypeVar("T")


class BaseSchema(Schema):
    TYPE_MAPPING = {
        datetime: CustomDateTimeField,
        date: CustomDateField,
    }


def validate_and_get_dataclass(data: Dict[str, Any], dataclass: Type[T]) -> T:
    schema_cls = class_schema(dataclass, base_schema=BaseSchema)
    schema = schema_cls()

    try:
        return cast(T, schema.load(data))
    except exceptions.ValidationError as e:
        raise ValidationError(e.messages)
