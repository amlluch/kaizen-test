import base64
import uuid
from dataclasses import asdict, dataclass
from typing import Iterable, Protocol, runtime_checkable

from kaizen_blog_api.errors import ImageError
from kaizen_blog_api.post.entities import Post
from kaizen_blog_api.post.repository import IPostRepository
from kaizen_blog_api.serializers import dict_factory
from kaizen_blog_api.validators import validate_and_get_dataclass


@dataclass
class CreatePostRequest:
    text: str
    username: str


@dataclass
class GetPostRequest:
    id: uuid.UUID


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
