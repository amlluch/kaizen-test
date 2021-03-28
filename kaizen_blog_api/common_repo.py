import uuid
from dataclasses import asdict
from typing import Any, Dict, Type, TypeVar

from boto3.dynamodb import conditions

from kaizen_blog_api.errors import RecordNotFound, RepositoryError
from kaizen_blog_api.serializers import dict_factory
from kaizen_blog_api.validators import validate_and_get_dataclass

T = TypeVar("T")


def get_record(record_id: uuid.UUID, dataclass: Type[T], table: Any) -> T:
    condition = conditions.Key("id").eq(str(record_id))
    result = table.query(KeyConditionExpression=condition)

    if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
        raise RepositoryError("error occurred when retrieving post details")

    if not result["Count"]:
        raise RecordNotFound(f"Record with id {record_id} was not found")
    return validate_and_get_dataclass(result["Items"][0], dataclass)


def request_to_insert(request: T) -> Dict:
    data = {name: value for name, value in asdict(request, dict_factory=dict_factory).items() if value is not None}
    data["id"] = uuid.uuid4()
    return data
