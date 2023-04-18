from typing import List

from pydantic import BaseModel


class PageHosts(BaseModel):
    items: List[str]
    total: int
    page: int
    size: int


class Host(BaseModel):
    name: str
    total_count: int
    remaining_daily_requests: int | None
