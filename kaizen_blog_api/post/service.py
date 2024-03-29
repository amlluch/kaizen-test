import base64
import uuid
from dataclasses import dataclass
from typing import Iterable, Protocol, runtime_checkable

from kink import inject

from kaizen_blog_api.common import BaseRequestClass, request_to_insert
from kaizen_blog_api.errors import ImageError
from kaizen_blog_api.post.entities import Post
from kaizen_blog_api.post.repository import IPostRepository
from kaizen_blog_api.validators import validate_and_get_dataclass


@dataclass
class CreatePostRequest:
    text: str
    username: str


@dataclass
class GetPostRequest(BaseRequestClass):
    pass


@dataclass
class LikePostRequest(BaseRequestClass):
    pass


class UpdateImageRequest:
    def __init__(self, post_id: str, image: str, is_base64_encoded: bool):
        self.image = image
        self.is_base64_encoded = is_base64_encoded
        self.post_id = uuid.UUID(post_id)


@runtime_checkable
class IPostService(Protocol):
    def create(self, request: CreatePostRequest) -> Post:
        ...

    def read(self, request: GetPostRequest) -> Post:
        ...

    def list_reversed(self) -> Iterable[Post]:
        ...

    def update_logo(self, request: UpdateImageRequest) -> Post:
        ...

    def like(self, request: LikePostRequest) -> Post:
        ...


@inject(alias=IPostService)
class PostService(IPostService):
    def __init__(self, repository: IPostRepository):
        self._repository = repository

    def create(self, request: CreatePostRequest) -> Post:
        data = request_to_insert(request)
        post = validate_and_get_dataclass(data, Post)
        self._repository.insert(post)
        return post

    def read(self, request: GetPostRequest) -> Post:
        return self._repository.get(request.id)

    def list_reversed(self) -> Iterable[Post]:
        posts = self._repository.list_by_date_reversed()
        for post in posts:
            yield post

    def update_logo(self, request: UpdateImageRequest) -> Post:
        if not request.image:
            raise ImageError("File should be an image")
        if request.is_base64_encoded:
            image = base64.b64decode(request.image)
        else:
            pos = request.image.find("base64,")
            if pos > 0:
                image = base64.b64decode(request.image[(pos + 7) :])  # noqa: E203
            else:
                raise ImageError("Invalid image file")

        post = self._repository.get(request.post_id)
        uploaded_image = self._repository.upload(image, request.post_id)
        post.image = uploaded_image
        self._repository.update(post, request.post_id)

        return self._repository.get(request.post_id)

    def like(self, request: LikePostRequest) -> Post:
        post = self._repository.get(request.id)
        post.likes += 1
        self._repository.update(post, request.id)
        return post
