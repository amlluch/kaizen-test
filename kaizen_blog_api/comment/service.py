import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from kaizen_blog_api import ADMIN_EMAIL_ADDRESS
from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.comment.repository import ICommentRepository
from kaizen_blog_api.common import request_to_insert
from kaizen_blog_api.events import CommentDeletedEvent, Event
from kaizen_blog_api.validators import validate_and_get_dataclass


@dataclass
class CreateCommentRequest:
    text: str
    username: str
    post_id: uuid.UUID


@dataclass
class DeleteCommentRequest:
    id: uuid.UUID


@runtime_checkable
class ICommentService(Protocol):
    def create(self, request: CreateCommentRequest) -> Comment:
        ...

    def delete(self, request: DeleteCommentRequest) -> None:
        ...

    def notify(self, request: Event) -> None:
        ...


class CommentService(ICommentService):
    def __init__(self, repository: ICommentRepository):
        self._repository = repository

    def create(self, request: CreateCommentRequest) -> Comment:
        data = request_to_insert(request)
        comment = validate_and_get_dataclass(data, Comment)
        self._repository.insert(comment)
        return comment

    def delete(self, request: DeleteCommentRequest) -> None:
        comment = self._repository.get(request.id)
        self._repository.delete(request.id)
        self._repository.dispatch_sns(CommentDeletedEvent(comment))

    def notify(self, request: Event) -> None:
        payload = json.loads(request.payload)
        payload["created_at"] = datetime.fromtimestamp(payload["created_at"])
        comment = validate_and_get_dataclass(payload, Comment)
        self._repository.send_email(ADMIN_EMAIL_ADDRESS, comment)
