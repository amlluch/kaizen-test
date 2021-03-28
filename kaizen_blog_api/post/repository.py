import uuid
from dataclasses import asdict, dataclass
from typing import Any, Protocol, runtime_checkable

from boto3.dynamodb import conditions
from botocore.exceptions import ClientError

from kaizen_blog_api.errors import AWSError, RecordNotFound, RepositoryError
from kaizen_blog_api.post.entities import Post
from kaizen_blog_api.serializers import dict_factory
from kaizen_blog_api.validators import validate_and_get_dataclass


@dataclass
class CreatePostRequest:
    text: str
    username: str


@runtime_checkable
class IPostRepository(Protocol):
    def insert(self, post: Post) -> None:
        ...

    def get(self, post_id: uuid.UUID) -> Post:
        ...


class PostRepository(IPostRepository):
    def __init__(self, posts_table: Any) -> None:
        self.table = posts_table

    def insert(self, post: Post) -> None:
        try:
            self.table.put_item(Item=asdict(post, dict_factory=dict_factory))
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} inserting {str(post.id)}") from e

    def get(self, post_id: uuid.UUID) -> Post:
        condition = conditions.Key("id").eq(str(post_id))
        result = self.table.query(KeyConditionExpression=condition)

        if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
            raise RepositoryError("error occurred when retrieving post details")

        if not result["Count"]:
            raise RecordNotFound(f"Post with id {post_id} was not found")
        post = validate_and_get_dataclass(result["Items"][0], Post)

        return post
