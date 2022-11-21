from typing import List
from uuid import UUID, uuid4

from fastapi import status


async def new_uuid() -> UUID:
    val = uuid4()
    while val.hex[0] == "0":
        val = uuid4()
    return val


async def get_status_code(items: List, total: int) -> int:
    if not items:
        return status.HTTP_404_NOT_FOUND

    if total > len(items):
        return status.HTTP_206_PARTIAL_CONTENT

    return status.HTTP_200_OK
