# Ecoindex-Api

This tool provides an easy way to analyze websites with [Ecoindex](http://www.ecoindex.fr) on a remote server. You have the ability to:

- Make a page analysis
- Define screen resolution
- Save results to a DB
- Retrieve results
- Limit the number of request per day for a given host

This API is built on top of [ecoindex-python](https://pypi.org/project/ecoindex/) with [FastAPI](https://fastapi.tiangolo.com/)

## OpenAPI specification

The API specification can be found in the [documentation](docs/openapi.json). You can also access it with [Redoc](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/cnumr/ecoindex_api/main/docs/openapi.json).

## Requirements

- [Docker](https://www.docker.com/)
- [Docker-compose](https://docs.docker.com/compose/)

With this docker setup you get 2 services running that are enough to make it all work:

- `db`: A MySQL instance
- `api`: The API instance running FastAPI application with [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)

```bash
cp docker-compose.yml.dist docker-compose.yml && \
docker-compose build && docker-compose up -d
```

Then you can go to [http://localhost:8001/docs](http://localhost:8001/docs) to access to the swagger

## Configuration

### Page wait

You can define a wait time after the page is loaded (before we simulate a scroll to the bottom) and a wait time after the page is scrolled to the bottom.

You have to set the environment variables `WAIT_BEFORE_SCROLL` and `WAIT_AFTER_SCROLL`. Default values are 3 seconds. For example:

```env
WAIT_BEFORE_SCROLL=1
WAIT_AFTER_SCROLL=1
```

### CORS

You can configure CORS to secure your API server. By default, all methods, origins and headers are authorized.

You have to set the environment variables `CORS_ALLOWED_HEADERS`, `CORS_ALLOWED_METHODS`, `CORS_ALLOWED_ORIGINS` and `CORS_ALLOWED_CREDENTIALS`. For example:

```env
CORS_ALLOWED_CREDENTIALS=True
CORS_ALLOWED_HEADERS=my-custom-header,other-custom-header
CORS_ALLOWED_METHODS=GET,POST,UPDATE
CORS_ALLOWED_ORIGINS=my.host.com,backup-host.com
```

### Daily limit per day

You can configure a daily limit per day for host by setting the environment variable `DAILY_LIMIT_PER_HOST`. When this variable is set, it won't be possible for a same host to make more request than defined in the same day to avoid overload.

If the variable is set, you will get a header `x-remaining-daily-requests: 6`

If you reach your authorized request quota for the day, the next requests will give you a response:

```http
HTTP/1.1 429 Too Many Requests
content-length: 99
content-type: application/json
date: Tue, 31 Aug 2021 13:08:20 GMT
server: uvicorn

{
    "detail": "You have already reached the daily limit of 10 requests for host www.ecoindex.fr today"
}
```

> If the variable is set to 0, no limit is set.

## Local development

If you need to test the API locally, you can easily run it. You have to use [Poetry](https://python-poetry.org/) to install dependencies and run `uvicorn` server.

```bash
poetry install && \
poetry run uvicorn api.main:app --reload --port 8001
```

> This way, you get a server running on [localhost:8001](http://localhost:8001/docs) with a local database saved in `./sql_app.dv`

## Testing

In order to develop or test, you have to use [Poetry](https://python-poetry.org/), install the dependencies and execute a poetry shell:

```bash
poetry install && \
poetry shell
```

We use Pytest to run unit tests for this project. The test suite are in the `tests` folder. Just execute :

```Bash
pytest --cov-report term-missing:skip-covered --cov=. --cov-config=.coveragerc tests
```

> This runs pytest and also generate a [coverage report](https://pytest-cov.readthedocs.io/en/latest/) (terminal and html)

## [Contributing](CONTRIBUTING.md)

## [Code of conduct](CODE_OF_CONDUCT.md)
