class PatchLibException(Exception):
    """Base exception for PatchLib"""


class InvalidPatchDefinitionError(PatchLibException):
    pass


class PatchProfileError(PatchLibException):
    pass


class PatchApiException(PatchLibException):
    def __init__(self, response):
        self.response = response

    def __repr__(self):
        return "{}('{}')".format(type(self).__name__, self.message)

    def __str__(self):
        return self.message


class ApiBadRequest(PatchApiException):
    """400 Error"""
    status_code = 400

    def __init__(self):
        self.message = '400 Bad Request'


class ApiNotAuthorized(PatchApiException):
    """401 Error"""
    status_code = 401

    def __init__(self):
        self.message = '401 Not Authorized'


class ApiForbidden(PatchApiException):
    """403 Error"""
    status_code = 403

    def __init__(self):
        self.message = '403 Forbidden'


class ApiNotFound(PatchApiException):
    """404 Error"""
    status_code = 404

    def __init__(self):
        self.message = '404 Not Found'
