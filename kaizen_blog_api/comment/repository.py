from dataclasses import asdict
from typing import Any, Protocol, runtime_checkable

from botocore.exceptions import ClientError

from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.errors import AWSError
from kaizen_blog_api.serializers import dict_factory


@runtime_checkable
class ICommentRepository(Protocol):
    def insert(self, comment: Comment) -> None:
        ...


class CommentRepository(ICommentRepository):
    def __init__(self, comments_table: Any):
        self.table = comments_table

    def insert(self, comment: Comment) -> None:
        try:
            self.table.put_item(Item=asdict(comment, dict_factory=dict_factory))
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} inserting {str(comment.id)}") from e
