import os
from logging import Logger
from os import environ

import boto3
from kink import di

from kaizen_blog_api.logger import create_logger

di[Logger] = create_logger(os.getenv("LOG_LEVEL", "INFO"))
di["dynamo_db"] = boto3.resource("dynamodb", region_name=environ.get("AWS_REGION", "eu-west-1"))

di["posts_table"] = di["dynamo_db"].Table(environ.get("POSTS_TABLE", "posts"))
