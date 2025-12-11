from pydantic import BaseModel


class FileSchema(BaseModel):
    filename: str
    url: str
    size: int
    content_type: str
