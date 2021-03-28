import uuid
from dataclasses import asdict, dataclass
from io import BytesIO
from typing import Any, Iterable, Optional, Protocol, runtime_checkable

from botocore.client import BaseClient
from botocore.exceptions import ClientError
from PIL import Image as ImageProcess, UnidentifiedImageError

from kaizen_blog_api.common_repo import get_record
from kaizen_blog_api.errors import AWSError, ImageError, RepositoryError
from kaizen_blog_api.post.entities import Image, Post
from kaizen_blog_api.serializers import dict_factory
from kaizen_blog_api.validators import validate_and_get_dataclass


@dataclass
class CreatePostRequest:
    text: str
    username: str


@runtime_checkable
class IPostRepository(Protocol):
    def insert(self, post: Post) -> None:
        ...

    def get(self, post_id: uuid.UUID) -> Post:
        ...

    def list_by_date_reversed(self) -> Iterable[Post]:
        ...

    def upload(self, image: bytes, key: uuid.UUID) -> Image:
        ...

    def update(self, post: Post = None, post_id: uuid.UUID = None) -> None:
        ...


class PostRepository(IPostRepository):
    def __init__(self, posts_table: Any, bucket_name: Optional[str], s3_client: Optional[BaseClient]) -> None:
        self.table = posts_table
        self._s3_client = s3_client
        self._bucket_name = bucket_name

    def insert(self, post: Post) -> None:
        try:
            self.table.put_item(Item=asdict(post, dict_factory=dict_factory))
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} inserting {str(post.id)}") from e

    def get(self, post_id: uuid.UUID) -> Post:
        return get_record(post_id, Post, self.table)

    def list_by_date_reversed(self) -> Iterable[Post]:
        result = self.table.scan(IndexName="by_date")
        if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
            raise RepositoryError("error occurred when retrieving post details")
        for item in reversed(result["Items"]):
            yield validate_and_get_dataclass(item, Post)

    def upload(self, image: bytes, key: uuid.UUID) -> Image:
        fp = BytesIO(image)

        try:
            img = ImageProcess.open(fp)
        except UnidentifiedImageError:
            raise ImageError("Unrecognizable image format.")

        fp.seek(0)
        image_format = img.format
        name = f"{key}.{image_format}".lower()
        url = f"https://{self._bucket_name}.s3.amazonaws.com/posts/{name}"
        assert self._s3_client

        try:
            self._s3_client.upload_fileobj(fp, self._bucket_name, f"posts/{key}", ExtraArgs={"ACL": "public-read"})
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} uploading image to S3") from e

        return Image(id=key, url=url)

    def update(self, post: Post = None, post_id: uuid.UUID = None) -> None:

        record = asdict(post, dict_factory=dict_factory)
        record.pop("id")
        update_set_expr = "set " + ", ".join(f"#{k} = :{k}" for k, v in record.items())
        attr_set_names = {f"#{k}": k for k, v in record.items()}
        attr_values = {f":{k}": v for k, v in record.items()}

        kwargs = dict(
            Key={"id": str(post_id)},
            UpdateExpression=update_set_expr,
            ExpressionAttributeValues=attr_values,
            ExpressionAttributeNames=attr_set_names,
            ReturnValues="ALL_NEW",
        )
        try:
            self.table.update_item(**{key: value for key, value in kwargs.items() if len(value)})
        except ClientError as e:
            raise AWSError(f"AWS error {e.response['Error']['Code']} updating record {str(post_id)}") from e
