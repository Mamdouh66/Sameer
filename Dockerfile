FROM python:3.11.4-slim-buster

RUN pip install poetry==1.8.1
RUN pip install uvicorn

ENV\
    POETRY_VIRTUALENVS_CREATE=false\
    POETRY_VITRUALENV_IN_PROJECT=false\
    POETRY_NO_INTERACTION=1\
    POETRY_VERSION=1.8.1

WORKDIR /app

COPY poetry.lock pyproject.toml ./

COPY Sameer ./Sameer

RUN poetry install

CMD [ "uvicorn", "Sameer.main:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--reload-include", "*"]
