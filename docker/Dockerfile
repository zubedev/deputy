FROM python:3.11-slim

RUN apt-get update && apt-get install --no-install-recommends -y \
    # dependencies for building Python packages \
    build-essential \
    # psycopg2 dependencies \
    libpq-dev \
    # wait script \
    wait-for-it \
    # cleaning up unused files \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VERSION=1.5.1

# install poetry
RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false

# set work directory as /deputy
WORKDIR /deputy

# install dependencies
COPY poetry.lock* pyproject.toml /deputy/
RUN poetry install --with=dev --no-interaction

# copy entry script
COPY docker/entrypoint /entrypoint
RUN chmod +x /entrypoint

# copy the start script
COPY docker/start /start
RUN chmod +x /start

# copy project
COPY . /deputy/

ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
