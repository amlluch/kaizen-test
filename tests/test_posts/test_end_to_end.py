import json
import uuid
from base64 import b64encode
from typing import Dict

import pytest

from kaizen_blog_api.controller import create_post, like_comment, list_posts, read_post, update_image
from kaizen_blog_api.post.service import PostService


class TestPost:
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test"}],
    )
    def test_create_post(self, body: Dict, post_service: PostService) -> None:
        # given
        service = post_service

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
    def test_read_post(self, body: Dict, post_service: PostService) -> None:
        # given
        event: Dict = {"body": json.dumps(body)}

        # when
        result = create_post(event, None, post_service)
        body = json.loads(result["body"])

        # then
        event = {"pathParameters": {"id": body["id"]}}
        response = read_post(event, None, post_service)

        assert response["statusCode"] == 200

    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test"}],
    )
    def test_read_post_not_existing_record(self, body: Dict, post_service: PostService) -> None:

        # given
        event = {"pathParameters": {"id": str(uuid.uuid4())}}
        response = read_post(event, None, post_service)

        # then
        assert response["statusCode"] == 404

    @pytest.mark.usefixtures("many_dummy_posts")
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    def test_list_posts(self, post_service: PostService) -> None:

        # when
        response = list_posts({}, None, post_service)

        # then
        body = json.loads(response["body"])
        assert body[0]["created_at"] > body[-1]["created_at"]

    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test"}],
    )
    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    def test_upload_image(self, body: Dict, image_bytes: bytes, post_service: PostService) -> None:

        # given
        event = {"body": json.dumps(body)}
        result = create_post(event, None, post_service)
        post_id = json.loads(result["body"])["id"]

        # when
        response = update_image(
            {
                "pathParameters": {"id": post_id},
                "body": b64encode(image_bytes),
                "isBase64Encoded": True,
            },
            {},
            post_service,
        )

        # then
        assert response["statusCode"] == 200, response
        body = json.loads(response["body"])
        assert "image" in body
        assert body["image"]["id"] == body["id"]

    @pytest.mark.usefixtures("dynamodb_tables_fixture")
    @pytest.mark.parametrize(
        "body",
        [{"text": "blog text", "username": "user test"}],
    )
    def test_like_comment(self, body: Dict, post_service: PostService) -> None:
        # given
        event: Dict = {"body": json.dumps(body)}

        # when
        result = create_post(event, None, post_service)
        body = json.loads(result["body"])

        # then
        event = {"pathParameters": {"id": body["id"]}}
        like_response = like_comment(event, None, post_service)
        assert like_response["statusCode"] == 200
        response = read_post(event, None, post_service)
        body = json.loads(response["body"])
        assert body["likes"] == 1
        assert response["statusCode"] == 200
