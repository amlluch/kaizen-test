import json
from dataclasses import asdict
from logging import Logger

from kink import inject

from kaizen_blog_api.custom_types import LambdaContext, LambdaEvent, LambdaResponse
from kaizen_blog_api.post.service import CreatePostRequest, IPostService
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
