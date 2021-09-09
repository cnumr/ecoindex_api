from datetime import date
from typing import Optional

from db.crud import (
    get_count_daily_request_per_host,
    get_ecoindex_result_list_db,
    save_ecoindex_result_db,
)
from db.database import create_db_and_tables, get_session
from ecoindex import get_page_analysis
from ecoindex.models import WebPage, WindowSize
from fastapi import FastAPI, Response, status
from fastapi.exceptions import HTTPException
from fastapi.params import Body, Depends, Query
from fastapi_pagination import Page, add_pagination, paginate
from selenium.common.exceptions import TimeoutException, WebDriverException
from settings import DAILY_LIMIT_PER_HOST
from sqlmodel import Session

from api.models import ApiEcoindex

app = FastAPI(
    title="Ecoindex API",
    version="1.0.0",
    description="Ecoindex API enables you to perform ecoindex analysis of given web pages",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post(
    "/v1/ecoindexes",
    response_model=ApiEcoindex,
    response_description="Corresponding ecoindex result",
    responses={
        429: {
            "description": "You have reached the daily limit",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "You have already reached the daily limit of 5 requests for host www.ecoindex.fr today"
                    }
                }
            },
        }
    },
    tags=["ecoindex"],
    description="This performs ecoindex analysis of a given webpage with a defined resolution",
    status_code=status.HTTP_201_CREATED,
)
def add_ecoindex_analysis(
    response: Response,
    session: Session = Depends(get_session),
    web_page: WebPage = Body(
        ...,
        title="Web page to analyze defined by its url and its screen resolution",
        example=WebPage(url="http://www.ecoindex.fr", width=1920, height=1080),
    ),
) -> ApiEcoindex:
    if DAILY_LIMIT_PER_HOST:
        count_daily_request_per_host = get_count_daily_request_per_host(
            session=session, host=web_page.url.host
        )
        response.headers["X-Remaining-Daily-Requests"] = str(
            DAILY_LIMIT_PER_HOST - count_daily_request_per_host - 1
        )

    if DAILY_LIMIT_PER_HOST and count_daily_request_per_host >= DAILY_LIMIT_PER_HOST:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You have already reached the daily limit of {DAILY_LIMIT_PER_HOST} requests for host {web_page.url.host} today",
        )
    try:
        web_page_result = get_page_analysis(
            url=web_page.url,
            window_size=WindowSize(height=web_page.height, width=web_page.width),
        )

    except (TimeoutException, WebDriverException) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.msg
        )
    db_result = save_ecoindex_result_db(
        session=session, ecoindex_result=web_page_result, version=1
    )

    return db_result


@app.get(
    "/v1/ecoindexes",
    response_model=Page[ApiEcoindex],
    response_description="List of corresponding ecoindex results",
    tags=["ecoindex"],
    description="This returns a list of ecoindex analysis corresponding to query filters. The results are ordered by ascending date",
)
def get_ecoindex_analysis_list(
    session: Session = Depends(get_session),
    date_from: Optional[date] = Query(
        None, description="Start date of the filter elements (example: 2020-01-01)"
    ),
    date_to: Optional[date] = Query(
        None, description="End date of the filter elements  (example: 2020-01-01)"
    ),
    host: Optional[str] = Query(None, description="Host name you want to filter"),
) -> Page[ApiEcoindex]:
    ecoindexes = get_ecoindex_result_list_db(
        session=session, date_from=date_from, date_to=date_to, host=host, version=1
    )
    return paginate(ecoindexes)


add_pagination(app)
