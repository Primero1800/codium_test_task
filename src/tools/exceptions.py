from fastapi import status


class CustomException(Exception):
    def __init__(self, msg: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.msg = msg
        self.status_code = status_code
