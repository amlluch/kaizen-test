import json
from typing import Dict

import boto3
import pytest

from kaizen_blog_api.controller import create_post
from kaizen_blog_api.post.repository import PostRepository
from kaizen_blog_api.post.service import PostService


class TestPost:
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test"}],
    )
    def test_create_post(self, body: Dict) -> None:
        # given
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        posts_table = dynamodb.Table("posts")
        repository = PostRepository(posts_table)
        service = PostService(repository)

        event = {"body": json.dumps(body)}
        # when
        result = create_post(event, None, service)
        assert result["statusCode"] == 200

    @pytest.mark.parametrize(
        "body",
        [
            {"text": "blog text", "username": "user test", "bad_field": "bad_value"},
            {"text": "blog text", "username": 3},
            {"text": "blog text"},
        ],
    )
    def test_create_post_fails(self, body: Dict) -> None:
        # given
        event = {"body": json.dumps(body)}
        result = create_post(event, None, PostService)

        # then
        assert result["statusCode"] == 422
