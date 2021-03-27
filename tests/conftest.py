import uuid
from dataclasses import asdict
from typing import Any

import boto3
import pytest
from moto import mock_dynamodb2

from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.post.entities import Image, Post
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
