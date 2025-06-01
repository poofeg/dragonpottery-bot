FROM python:3.13-alpine AS builder

RUN python -m venv /opt/poetry
RUN /opt/poetry/bin/pip install --no-cache-dir -U pip setuptools
RUN /opt/poetry/bin/pip install --no-cache-dir poetry
RUN ln -svT /opt/poetry/bin/poetry /usr/local/bin/poetry
RUN poetry config virtualenvs.in-project true


FROM builder AS build
WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --no-cache --no-interaction --no-ansi --no-root --without=dev

COPY dragonpottery_bot dragonpottery_bot
RUN poetry install --no-cache --no-interaction --no-ansi --without=dev


FROM python:3.13-alpine AS main

WORKDIR /app
COPY --from=build /app /app
CMD ["/app/.venv/bin/dragonpottery-bot"]
