import json
import uuid
from dataclasses import asdict
from typing import Dict

import pytest

from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.comment.service import CommentService
from kaizen_blog_api.controller import admin_notify, create_comment, delete_comment, list_comments, read_comment
from kaizen_blog_api.events import CommentDeletedEvent


class TestComment:
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test", "post_id": str(uuid.uuid4())}],
    )
    def test_create_comment(self, body: Dict, comment_service: CommentService) -> None:
        # given

        event = {"body": json.dumps(body)}
        # when
        result = create_comment(event, None, comment_service)
        assert result["statusCode"] == 200

    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test", "post_id": str(uuid.uuid4())}],
    )
    def test_delete_comment(self, body: Dict, comment_service: CommentService) -> None:

        event: Dict = {"body": json.dumps(body)}
        # given
        result = create_comment(event, None, comment_service)
        body = json.loads(result["body"])

        # then
        event = {"pathParameters": {"id": str(body["id"])}}
        response = delete_comment(event, None, comment_service)
        assert response["statusCode"] == 204

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
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    def test_notify_deleted_comment(self, body: Dict, comment_service: CommentService) -> None:

        event: Dict = {"Records": [{"Sns": {"Message": json.dumps(body)}}]}
        admin_notify(event, None, comment_service)

    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test", "post_id": str(uuid.uuid4())}],
    )
    def test_read_comment(self, body: Dict, comment_service: CommentService) -> None:

        event: Dict = {"body": json.dumps(body)}
        # given
        result = create_comment(event, None, comment_service)
        body = json.loads(result["body"])

        # then
        event = {"pathParameters": {"id": body["id"]}}
        response = read_comment(event, None, comment_service)
        assert response["statusCode"] == 200
        ...

    @pytest.mark.usefixtures("many_dummy_comments")
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    def test_list_posts(self, comment_service: CommentService) -> None:

        # when
        response = list_comments({}, None, comment_service)

        # then
        body = json.loads(response["body"])
        assert body[0]["created_at"] > body[-1]["created_at"]
