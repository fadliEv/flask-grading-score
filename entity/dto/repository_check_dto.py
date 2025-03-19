from pydantic import BaseModel
from typing import Optional

class RepositoryCheckRequest(BaseModel):
    repository_url: str
    branch: Optional[str] = "master"