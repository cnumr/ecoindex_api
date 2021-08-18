from ecoindex import get_page_analysis
from ecoindex.models import WebPage, WindowSize
from fastapi import FastAPI, Response, status
from fastapi.exceptions import HTTPException
from fastapi.params import Body, Depends
from fastapi_pagination import Page, add_pagination, paginate
from selenium.common.exceptions import TimeoutException, WebDriverException
from sqlalchemy.orm.session import Session

from api.models import ApiResult
from db.crud import (
    get_count_daily_request_per_host,
    get_ecoindex_result_list_db,
    save_ecoindex_result_db,
)
from db.database import SessionLocal, engine
from db.models import Base
from settings import DAILY_LIMIT_PER_HOST

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(
    title="Ecoindex API",
    version="1.0.0",
    description="Ecoindex API enables you to perform ecoindex analysis of given web pages",
)


@app.post(
    "/v1/ecoindexes",
    response_model=ApiResult,
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
    web_page: WebPage = Body(
        ...,
        title="Web page to analyze defined by its url and its screen resolution",
        example=WebPage(url="http://www.ecoindex.fr", width=1920, height=1080),
    ),
    db: Session = Depends(get_db),
) -> ApiResult:
    if DAILY_LIMIT_PER_HOST:
        count_daily_request_per_host = get_count_daily_request_per_host(
            db=db, host=web_page.url.host
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

    # TODO: WebDriver exception -> Erreur 400...
    except (TimeoutException, WebDriverException) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.msg
        )
    db_result = save_ecoindex_result_db(db=db, ecoindex_result=web_page_result)

    return db_result


# TODO: Filtres: Date ? Limit ? Offset ? Host ?
# TODO: Top 10 du jour ? pour un host donné ?
@app.get(
    "/v1/ecoindexes",
    response_model=Page[ApiResult],
    response_description="List of corresponding ecoindex results",
    tags=["ecoindex"],
    description="This performs ecoindex analysis of a list of given webpages with a defined resolution",
)
def get_ecoindex_analysis_list(
    db: Session = Depends(get_db),
) -> Page[ApiResult]:
    ecoindexes = get_ecoindex_result_list_db(db=db)
    return paginate(ecoindexes)


add_pagination(app)
