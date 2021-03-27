import uuid
from dataclasses import asdict

from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.serializers import dict_factory


def test_can_instantiate() -> None:
    # given
    comment = Comment(id=uuid.uuid4(), text="testing", username="user test", post_id=uuid.uuid4())

    # then
    assert isinstance(comment, Comment)


def test_serialize(dummy_comment: Comment) -> None:
    # given
    comment = asdict(dummy_comment, dict_factory=dict_factory)

    # then
    assert isinstance(comment["id"], str)
    assert isinstance(comment["post_id"], str)
    assert isinstance(comment["created_at"], int)
