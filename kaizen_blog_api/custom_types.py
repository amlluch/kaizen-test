from typing import Any, Dict

from aws_lambda_context import LambdaContext as Context

LambdaEvent = Dict[str, Any]
LambdaContext = Context
LambdaResponse = Dict[str, Any]
