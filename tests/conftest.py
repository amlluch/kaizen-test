import uuid
from dataclasses import asdict
from typing import Any

import boto3
import pytest
from moto import mock_dynamodb2, mock_s3, mock_ses, mock_sns

from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.comment.repository import CommentRepository
from kaizen_blog_api.comment.service import CommentService
from kaizen_blog_api.post.entities import Image, Post
from kaizen_blog_api.post.repository import PostRepository
from kaizen_blog_api.post.service import PostService
from kaizen_blog_api.serializers import dict_factory


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


@pytest.fixture(scope="function")
def dynamodb_tables_fixture() -> Any:
    with mock_dynamodb2():
        posts_table_name = "posts"
        comments_table_name = "comments"

        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        dynamodb_client = boto3.client("dynamodb", region_name="eu-west-1")

        dynamodb.create_table(
            TableName=posts_table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "by_date",
                    "KeySchema": [
                        {"AttributeName": "id", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "N"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        dynamodb.create_table(
            TableName=comments_table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "by_date",
                    "KeySchema": [
                        {"AttributeName": "id", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "N"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        yield

        dynamodb_client.delete_table(TableName=posts_table_name)
        dynamodb_client.delete_table(TableName=comments_table_name)


@pytest.mark.usefixtures("dynamodb_tables_fixture")
@pytest.fixture()
def many_dummy_posts() -> None:
    dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
    posts_table = dynamodb.Table("posts")

    for num in range(25):
        post = Post(id=uuid.uuid4(), text=f"Post number {num}", username=f"user {num}")
        posts_table.put_item(Item=asdict(post, dict_factory=dict_factory))


@pytest.fixture()
def image_bytes() -> bytes:
    return b"GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;"


@pytest.mark.usefixtures("dynamodb_tables_fixture")
@pytest.fixture()
def many_dummy_comments() -> None:
    dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
    posts_table = dynamodb.Table("comments")

    for num in range(25):
        comment = Comment(id=uuid.uuid4(), text=f"Post number {num}", username=f"user {num}", post_id=uuid.uuid4())
        posts_table.put_item(Item=asdict(comment, dict_factory=dict_factory))


@pytest.fixture()
def post_service() -> PostService:

    dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
    posts_table = dynamodb.Table("posts")
    with mock_s3():
        bucket_name = "testing"
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3 = boto3.resource("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=bucket_name)
    repository = PostRepository(posts_table, bucket_name, s3_client)
    return PostService(repository)


@pytest.fixture()
def comment_service() -> CommentService:
    dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
    table = dynamodb.Table("comments")
    with mock_sns():
        sns = boto3.client("sns", region_name="eu-west-1")
        sns.create_topic(Name="testing")
    with mock_ses():
        ses = boto3.client("ses", region_name="eu-west-1")
        ses.verify_email_identity(EmailAddress="amlluch@gmail.com")
    repository = CommentRepository(table, sns, ses_client=ses)
    return CommentService(repository)
