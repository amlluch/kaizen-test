import uuid
from dataclasses import asdict, dataclass
from typing import Protocol, runtime_checkable

from kaizen_blog_api.post.entities import Post
from kaizen_blog_api.post.repository import IPostRepository
from kaizen_blog_api.serializers import dict_factory
from kaizen_blog_api.validators import validate_and_get_dataclass


@dataclass
class CreatePostRequest:
    text: str
    username: str


@runtime_checkable
class IPostService(Protocol):
    def create(self, request: CreatePostRequest) -> Post:
        ...


class PostService(IPostService):
    def __init__(self, repository: IPostRepository):
        self._repository = repository

    def create(self, request: CreatePostRequest) -> Post:
        post_data = {
            name: value for name, value in asdict(request, dict_factory=dict_factory).items() if value is not None
        }
        post_data["id"] = uuid.uuid4()

        post = validate_and_get_dataclass(post_data, Post)
        self._repository.insert(post)
        return post
