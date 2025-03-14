from pydantic import BaseModel, HttpUrl
from typing import Optional

class RepositoryCheckRequest(BaseModel):
    repository_url: str
    branch: Optional[str] = "master"

class RepositoryCheckResponse(BaseModel):
    status: str
    data: list
    error: Optional[str] = None
