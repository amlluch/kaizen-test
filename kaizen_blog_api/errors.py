class ApiError(RuntimeError):
    status_code = 500


class AWSError(ApiError):
    status_code = 500


class ValidationError(Exception):
    status_code = 422


class RepositoryError(ApiError):
    status_code = 417


class RecordNotFound(ApiError):
    status_code = 404
