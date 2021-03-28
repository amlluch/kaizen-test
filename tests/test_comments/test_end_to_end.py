import json
import uuid
from dataclasses import asdict
from typing import Dict

import boto3
import pytest
from moto import mock_ses, mock_sns

from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.comment.repository import CommentRepository
from kaizen_blog_api.comment.service import CommentService
from kaizen_blog_api.controller import admin_notify, create_comment, delete_comment
from kaizen_blog_api.events import CommentDeletedEvent


class TestComment:
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test", "post_id": str(uuid.uuid4())}],
    )
    def test_create_comment(self, body: Dict) -> None:
        # given
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        table = dynamodb.Table("comments")
        repository = CommentRepository(table, None, None)
        service = CommentService(repository)

        event = {"body": json.dumps(body)}
        # when
        result = create_comment(event, None, service)
        assert result["statusCode"] == 200

    @mock_sns
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test", "post_id": str(uuid.uuid4())}],
    )
    def test_delete_comment(self, body: Dict) -> None:

        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        table = dynamodb.Table("comments")
        sns = boto3.client("sns", region_name="eu-west-1")
        sns.create_topic(Name="testing")
        repository = CommentRepository(table, sns, None)
        service = CommentService(repository)

        event: Dict = {"body": json.dumps(body)}
        # given
        result = create_comment(event, None, service)
        body = json.loads(result["body"])

        # then
        event = {"pathParameters": {"id": str(body["id"])}}
        response = delete_comment(event, None, service)
        assert response["statusCode"] == 204

    @mock_ses
    @pytest.mark.parametrize(
        "body",
        [
            asdict(
                CommentDeletedEvent(
                    Comment(id=uuid.uuid4(), username="user test", text="text test", post_id=uuid.uuid4())
                )
            )
        ],
    )
    def test_notify_deleted_comment(self, body: Dict) -> None:
        ses = boto3.client("ses", region_name="eu-west-1")
        ses.verify_email_identity(EmailAddress="amlluch@gmail.com")
        repository = CommentRepository(None, None, ses)
        event: Dict = {"Records": [{"Sns": {"Message": json.dumps(body)}}]}
        service = CommentService(repository)
        admin_notify(event, None, service)
