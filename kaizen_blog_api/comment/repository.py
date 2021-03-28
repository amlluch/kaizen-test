import json
import uuid
from dataclasses import asdict
from typing import Any, Protocol, runtime_checkable

from botocore.exceptions import ClientError

from kaizen_blog_api import SNS_ARN
from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.common_repo import get_record
from kaizen_blog_api.errors import AWSError
from kaizen_blog_api.events import Event
from kaizen_blog_api.serializers import dict_factory


@runtime_checkable
class ICommentRepository(Protocol):
    def insert(self, comment: Comment) -> None:
        ...

    def dispatch_sns(self, event: Event) -> None:
        ...

    def get(self, comment_id: uuid.UUID) -> Comment:
        ...

    def delete(self, comment_id: uuid.UUID) -> None:
        ...


class CommentRepository(ICommentRepository):
    def __init__(self, comments_table: Any, sns_client: Any):
        self.table = comments_table
        self.sns = sns_client

    def insert(self, comment: Comment) -> None:
        try:
            self.table.put_item(Item=asdict(comment, dict_factory=dict_factory))
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} inserting {str(comment.id)}") from e

    def dispatch_sns(self, event: Event) -> None:
        message_attributes = {"action": {"DataType": "String", "StringValue": event.name}}
        self.sns.publish(
            TopicArn=SNS_ARN,
            Message=json.dumps({"default": json.dumps(asdict(event))}),
            MessageStructure="json",
            MessageAttributes=message_attributes,
        )

    def get(self, comment_id: uuid.UUID) -> Comment:
        return get_record(comment_id, Comment, self.table)

    def delete(self, comment_id: uuid.UUID) -> None:
        try:
            self.table.delete_item(Key={"id": str(comment_id)})
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} updating record {str(comment_id)}") from e
