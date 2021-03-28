import os
from logging import Logger
from os import environ

import boto3
from kink import di

from kaizen_blog_api.logger import create_logger

di["s3_client"] = boto3.client("s3")
di["bucket_name"] = environ.get("OFFERS_IMAGES_BUCKET", "images")

di[Logger] = create_logger(os.getenv("LOG_LEVEL", "INFO"))
di["dynamo_db"] = boto3.resource("dynamodb", region_name=environ.get("AWS_REGION", "eu-west-1"))

di["posts_table"] = di["dynamo_db"].Table(environ.get("POSTS_TABLE", "posts"))
di["sns_client"] = boto3.client("sns")

SNS_ARN = os.getenv("SNS_ARN", "arn:aws:sns:eu-west-1:123456789012:testing")
