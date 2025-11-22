FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR="/opt/poetry-cache" \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

FROM python:3.12-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY startup_scripts/ /app/startup_scripts/
RUN chmod +x /app/startup_scripts/entrypoint.sh \
    && chmod +x /app/startup_scripts/wait-for-it.sh

COPY . /app/

ENTRYPOINT ["/app/startup_scripts/entrypoint.sh"]
