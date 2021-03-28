import uuid
from dataclasses import asdict, dataclass
from typing import Protocol, runtime_checkable

from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.comment.repository import ICommentRepository
from kaizen_blog_api.serializers import dict_factory
from kaizen_blog_api.validators import validate_and_get_dataclass


@dataclass
class CreateCommentRequest:
    text: str
    username: str
    post_id: uuid.UUID


@runtime_checkable
class ICommentService(Protocol):
    def create(self, request: CreateCommentRequest) -> Comment:
        ...


class CommentService(ICommentService):
    def __init__(self, repository: ICommentRepository):
        self._repository = repository

    def create(self, request: CreateCommentRequest) -> Comment:
        comment_data = {
            name: value for name, value in asdict(request, dict_factory=dict_factory).items() if value is not None
        }
        comment_data["id"] = uuid.uuid4()

        comment = validate_and_get_dataclass(comment_data, Comment)
        self._repository.insert(comment)
        return comment
