from typing import List

from pydantic import BaseModel


class PageHosts(BaseModel):
    items: List[str]
    total: int
    page: int
    size: int
