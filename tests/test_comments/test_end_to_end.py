import json
import uuid
from typing import Dict

import boto3
import pytest

from kaizen_blog_api.comment.repository import CommentRepository
from kaizen_blog_api.comment.service import CommentService
from kaizen_blog_api.controller import create_comment


class TestComment:
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test", "post_id": str(uuid.uuid4())}],
    )
    def test_create_post(self, body: Dict) -> None:
        # given
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        posts_table = dynamodb.Table("posts")
        repository = CommentRepository(posts_table)
        service = CommentService(repository)

        event = {"body": json.dumps(body)}
        # when
        result = create_comment(event, None, service)
        assert result["statusCode"] == 200
