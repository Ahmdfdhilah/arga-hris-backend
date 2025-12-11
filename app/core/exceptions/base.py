class APIException(Exception):
    """Base exception with status_code and message"""
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
