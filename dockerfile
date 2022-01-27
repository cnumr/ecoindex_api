FROM python:3.8-slim as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.8-slim
WORKDIR /code
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN apt-get update && apt-get -y install libpq-dev gcc wget
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install psycopg2
COPY ./ /code/
COPY ./docker/entrypoint.sh /usr/bin/entrypoint
RUN chmod +x /usr/bin/entrypoint
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb
ENTRYPOINT [ "/usr/bin/entrypoint" ]