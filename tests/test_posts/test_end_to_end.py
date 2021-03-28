import json
import uuid
from typing import Dict

import boto3
import pytest

from kaizen_blog_api.controller import create_post, list_posts, read_post
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

    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test"}],
    )
    def test_read_post(self, body: Dict) -> None:
        # given
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        posts_table = dynamodb.Table("posts")
        repository = PostRepository(posts_table)
        service = PostService(repository)
        event: Dict = {"body": json.dumps(body)}

        # when
        result = create_post(event, None, service)
        body = json.loads(result["body"])

        # then
        event = {"pathParameters": {"id": body["id"]}}
        response = read_post(event, None, service)

        assert response["statusCode"] == 200

    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test"}],
    )
    def test_read_post_not_existing_record(self, body: Dict) -> None:

        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        posts_table = dynamodb.Table("posts")
        repository = PostRepository(posts_table)
        service = PostService(repository)

        # given
        event = {"pathParameters": {"id": str(uuid.uuid4())}}
        response = read_post(event, None, service)

        # then
        assert response["statusCode"] == 404

    @pytest.mark.usefixtures("many_dummy_posts")
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    def test_list_posts(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        posts_table = dynamodb.Table("posts")
        repository = PostRepository(posts_table)
        service = PostService(repository)

        # when
        response = list_posts({}, None, service)

        # then
        body = json.loads(response["body"])
        assert body[0]["created_at"] > body[-1]["created_at"]
