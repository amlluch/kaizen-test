import json
from functools import wraps
from typing import Any

from kaizen_blog_api.errors import ApiError, AWSError, ValidationError


def serverless(serverless_handler: Any) -> Any:
    def _inner(fn: Any) -> Any:
        @wraps(fn)
        def execute_serverless(*args, **kwargs):  # type: ignore
            try:
                return fn(*args, **kwargs)
            except AWSError as e:
                return {
                    "statusCode": e.status_code,
                    "body": '{"error": "' + str(e) + '"}',
                }
            except ApiError as e:
                return {
                    "statusCode": e.status_code,
                    "body": '{"error": "' + str(e) + '"}',
                }
            except ValidationError as e:
                body = {"error": str(e)}
                return {"statusCode": e.status_code, "body": json.dumps(body)}
            except Exception as e:
                return {"statusCode": 500, "body": '{"error": "' + str(e) + '"}'}

        return execute_serverless

    if serverless_handler is None:
        return _inner

    return _inner(serverless_handler)
