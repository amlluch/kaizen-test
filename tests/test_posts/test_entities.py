import uuid
from dataclasses import asdict

import pytest

from kaizen_blog_api.errors import ValidationError
from kaizen_blog_api.post.entities import Image, Post
from kaizen_blog_api.serializers import dict_factory


def test_can_instantiate_without_image() -> None:
    # given
    post = Post(
        id=uuid.uuid4(),
        text="testing",
        username="user test",
    )

    # then
    assert isinstance(post, Post)


def test_can_instantiate_with_image() -> None:
    # given

    post_id = uuid.uuid4()
    post = Post(
        id=post_id,
        text="testing",
        image=Image(id=post_id, url="https://fake.url"),
        username="user test",
    )

    # then
    assert isinstance(post, Post)


def test_cant_instantiate_wrong_image() -> None:
    # given
    with pytest.raises(ValidationError):
        Post(
            id=uuid.uuid4(),
            text="testing",
            image=Image(id=uuid.uuid4(), url="https://fake.url"),
            username="user test",
        )


def test_serialize_with_image(dummy_post: Post) -> None:
    # given
    post = asdict(dummy_post, dict_factory=dict_factory)

    # then
    assert isinstance(post["image"]["id"], str)


def test_serialize_without_image(dummy_post: Post) -> None:
    # given
    dummy_post.image = None
    post = asdict(dummy_post, dict_factory=dict_factory)

    # then
    assert isinstance(post["id"], str)
    assert isinstance(post["likes"], int)
