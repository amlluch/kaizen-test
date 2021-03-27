from dataclasses import asdict, dataclass
from typing import Any, Protocol, runtime_checkable

from botocore.exceptions import ClientError

from kaizen_blog_api.errors import AWSError
from kaizen_blog_api.post.entities import Post
from kaizen_blog_api.serializers import dict_factory


@dataclass
class CreatePostRequest:
    text: str
    username: str


@runtime_checkable
class IPostRepository(Protocol):
    def insert(self, post: Post) -> None:
        ...


class PostRepository(IPostRepository):
    def __init__(self, posts_table: Any) -> None:
        self.table = posts_table

    def insert(self, post: Post) -> None:
        try:
            self.table.put_item(Item=asdict(post, dict_factory=dict_factory))
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} inserting {str(post.id)}") from e
