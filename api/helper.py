import re
from typing import List
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from pydantic import BaseModel

from api.models.sort import Sort


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


async def get_sort_parameters(query_params: list[str], model: BaseModel) -> list[Sort]:
    validation_error = []
    result = []

    for query_param in query_params:
        pattern = re.compile("^\w+:(asc|desc)$")

        if not re.fullmatch(pattern, query_param):
            validation_error.append(
                {
                    "loc": ["query", "sort", query_param],
                    "message": "this parameter does not respect the sort format",
                    "type": "value_error.sort",
                }
            )
            continue

        sort_params = query_param.split(":")

        if sort_params[0] not in model.__fields__:
            validation_error.append(
                {
                    "loc": ["query", "sort", sort_params[0]],
                    "message": "this parameter does not exist",
                    "type": "value_error.sort",
                }
            )

        result.append(Sort(clause=sort_params[0], sort=sort_params[1]))

    if validation_error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=validation_error
        )

    return result
