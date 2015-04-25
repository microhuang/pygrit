# -*- coding: utf-8 -*-

class InvalidGitRepositoryError(BaseException):
    pass

class NoSuchPathError(BaseException):
    pass

class InvalidObjectTypeError(BaseException):
    pass

class GitTimeout(RuntimeError):
    pass
