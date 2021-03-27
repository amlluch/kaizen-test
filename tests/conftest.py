import uuid

import pytest

from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.post.entities import Image, Post


@pytest.fixture()
def dummy_post() -> Post:
    post_id = uuid.uuid4()
    return Post(
        id=post_id,
        text="testing",
        image=Image(id=post_id, url="https://fake.url"),
        username="user test",
    )


@pytest.fixture()
def dummy_comment() -> Comment:
    return Comment(id=uuid.uuid4(), text="testing comment", username="user test", post_id=uuid.uuid4())
