from enum import Enum, unique


@unique
class ErrorCodes(Enum):
    UserNotFound = 100
