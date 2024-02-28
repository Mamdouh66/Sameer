FROM python:3.11.4-slim-buster

RUN pip install poetry==1.8.1
RUN pip install uvicorn

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

COPY filmora ./filmora

RUN poetry install

ENTRYPOINT [ "uvicorn", "filmora.main:app", "--host", "0.0.0.0", "--port", "80"]