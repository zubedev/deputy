FROM python:3.11-slim

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update -y  \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    # dependencies for building packages
    build-essential \
    # psycopg dependencies
    libpq-dev \
    # wait script
    wait-for-it \
    # process manager
    supervisor

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VERSION=1.5.1

# install poetry
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install "poetry==$POETRY_VERSION" \
    && poetry config virtualenvs.create false

# set work directory as /deputy
WORKDIR /deputy

# install dependencies
COPY poetry.lock* pyproject.toml /deputy/
RUN --mount=type=cache,target=/root/.cache/pip \
    poetry install --with=dev --no-interaction

# remove packages that are not needed anymore
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip

# copy entry script
COPY docker/dev/entrypoint /entrypoint
RUN sed -i "s/\r$//g" /entrypoint \
    && chmod +x /entrypoint

# copy the start script
COPY docker/dev/start /start
RUN sed -i "s/\r$//g" /start \
    && chmod +x /start

# copy the supervisord config
COPY docker/dev/supervisord.conf /etc/supervisor/supervisord.conf

# copy project
COPY . .

ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
