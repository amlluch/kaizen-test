import json
import uuid
from dataclasses import asdict
from typing import Iterable, Protocol, runtime_checkable

from botocore.client import BaseClient
from botocore.exceptions import ClientError
from kink import inject

from kaizen_blog_api import SNS_ARN
from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.common import get_record
from kaizen_blog_api.errors import AWSError, RepositoryError
from kaizen_blog_api.events import Event
from kaizen_blog_api.serializers import dict_factory
from kaizen_blog_api.validators import validate_and_get_dataclass


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

    def send_email(self, recipient: str, comment: Comment) -> None:
        ...

    def list_by_date_reversed(self) -> Iterable[Comment]:
        ...


@inject(alias=ICommentRepository)
class CommentRepository(ICommentRepository):
    def __init__(self, comments_table: BaseClient, sns_client: BaseClient, ses_client: BaseClient):
        self.table = comments_table
        self.sns = sns_client
        self.ses = ses_client

    def insert(self, comment: Comment) -> None:
        try:
            self.table.put_item(Item=asdict(comment, dict_factory=dict_factory))
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} inserting {str(comment.id)}") from e

    def dispatch_sns(self, event: Event) -> None:
        message_attributes = {"action": {"DataType": "String", "StringValue": event.name}}
        self.sns.publish(
            TopicArn=SNS_ARN,
            Message=json.dumps({"default": json.dumps(asdict(event, dict_factory=dict_factory))}),
            MessageStructure="json",
            MessageAttributes=message_attributes,
        )

    def get(self, comment_id: uuid.UUID) -> Comment:
        return get_record(comment_id, Comment, self.table)

    def list_by_date_reversed(self) -> Iterable[Comment]:
        result = self.table.scan(IndexName="by_date")
        if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
            raise RepositoryError("error occurred when retrieving post details")
        for item in reversed(result["Items"]):
            yield validate_and_get_dataclass(item, Comment)

    def delete(self, comment_id: uuid.UUID) -> None:
        try:
            self.table.delete_item(Key={"id": str(comment_id)})
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} updating record {str(comment_id)}") from e

    def send_email(self, recipient: str, comment: Comment, sender: str = None) -> None:
        source = "amlluch@gmail.com" if sender is None else sender
        destination = {
            "ToAddresses": [
                recipient,
            ],
        }
        subject = f"Comment on post {comment.post_id} was deleted"
        body_text = f"The comment was created at {comment.created_at} by user {comment.username} with next text:\n\n{comment.text}"
        body_html = f"""<html>
        <head></head>
        <body>
          <h1>The comment was created at {comment.created_at} by user {comment.username}</h1>
          <p>{comment.text}</p>
        </body>
        </html>
                    """
        charset = "UTF-8"

        message = {
            "Body": {
                "Html": {
                    "Charset": charset,
                    "Data": body_html,
                },
                "Text": {
                    "Charset": charset,
                    "Data": body_text,
                },
            },
            "Subject": {
                "Charset": charset,
                "Data": subject,
            },
        }
        try:
            self.ses.send_email(Destination=destination, Message=message, Source=source)
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} sending email to admin") from e
