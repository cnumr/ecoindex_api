from ctypes import Union
from statistics import median

from fastapi_pagination import request
from pydantic import BaseModel


class Values(BaseModel):
    min: Union[float, int]
    max: Union[float, int]
    median: Union[float, int]


class ApiStatistic(BaseModel):
    dom: Values
    request: Values
    size: Values
