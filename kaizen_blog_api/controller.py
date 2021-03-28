import json
from dataclasses import asdict
from logging import Logger

from kink import inject

from kaizen_blog_api.custom_types import LambdaContext, LambdaEvent, LambdaResponse
from kaizen_blog_api.post.service import CreatePostRequest, GetPostRequest, IPostService, UpdateImageRequest
from kaizen_blog_api.serializers import JSONEncoder
from kaizen_blog_api.serverless import serverless
from kaizen_blog_api.validators import validate_and_get_dataclass


@serverless
@inject
def create_post(event: LambdaEvent, context: LambdaContext, service: IPostService, logger: Logger) -> LambdaResponse:
    logger.debug(event)
    logger.debug(context)

    request = validate_and_get_dataclass(json.loads(event["body"]), CreatePostRequest)
    result = service.create(request)

    return {
        "statusCode": 200,
        "body": json.dumps(asdict(result), cls=JSONEncoder),
    }


@serverless
@inject
def read_post(event: LambdaEvent, context: LambdaContext, service: IPostService, logger: Logger) -> LambdaResponse:
    logger.debug(event)
    logger.debug(context)

    request = validate_and_get_dataclass(event.get("pathParameters") or {}, GetPostRequest)
    result = service.read(request)

    return {
        "statusCode": 200,
        "body": json.dumps(asdict(result), cls=JSONEncoder),
    }


@serverless
@inject
def list_posts(event: LambdaEvent, context: LambdaContext, service: IPostService, logger: Logger) -> LambdaResponse:
    logger.debug(event)
    logger.debug(context)

    result = service.list_reversed()

    return {
        "statusCode": 200,
        "body": json.dumps([asdict(post) for post in result], cls=JSONEncoder),
    }


@serverless
@inject
def update_image(event: LambdaEvent, context: LambdaContext, service: IPostService, logger: Logger) -> LambdaResponse:
    logger.debug(event)
    logger.debug(context)

    post_id = event["pathParameters"]["id"]
    body = event["body"]
    is_base64_encoded = event["isBase64Encoded"]
    request = UpdateImageRequest(post_id, body, is_base64_encoded)
    resource = service.update_logo(request)
    return {"statusCode": 200, "body": json.dumps(asdict(resource), cls=JSONEncoder)}
