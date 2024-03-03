FROM python:3.11-slim as requirements

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update -y  \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    # dependencies for building packages
    build-essential \
    # psycopg dependencies
    libpq-dev

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VERSION=1.8.2

# set work directory as /deputy
WORKDIR /requirements
# copy over the files needed for poetry
COPY poetry.lock* pyproject.toml ./

# install poetry, export requirements
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install "poetry==$POETRY_VERSION" \
    && poetry export --without dev --without-hashes -f requirements.txt --output requirements.txt

# create a virtual environment and install dependencies
RUN python -m venv /venv
# set python to use the virtual environment
ENV PATH="/venv/bin:$PATH"
# install dependencies to the virtual environment
RUN --mount=type=cache,target=/root/.cache/pip \
    /venv/bin/python -m pip install -r requirements.txt

FROM python:3.11-slim

RUN apt-get update -y  \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    # psycopg dependencies
    libpq-dev \
    # wait script
    wait-for-it \
    # process manager
    supervisor \
    # clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 999 deputy  \
    && useradd -l -r -u 999 -g deputy deputy

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# copy over the virtual environment
COPY --from=requirements --chown=deputy:deputy /venv /venv
# set python to use the virtual environment
ENV PATH="/venv/bin:$PATH"

# set work directory as /deputy
RUN mkdir /deputy \
    && chown deputy:deputy /deputy
WORKDIR /deputy

# copy entry script
COPY --chown=deputy:deputy docker/prod/entrypoint /entrypoint
RUN sed -i "s/\r$//g" /entrypoint \
    && chmod +x /entrypoint

# copy the start script
COPY --chown=deputy:deputy docker/prod/start /start
RUN sed -i "s/\r$//g" /start \
    && chmod +x /start

# copy the supervisord config and gunicorn config
COPY --chown=deputy:deputy docker/prod/gunicorn.conf.py /deputy/gunicorn.conf.py
COPY --chown=deputy:deputy docker/prod/supervisord.conf /etc/supervisor/supervisord.conf

# copy project and remove unnecessary files
COPY --chown=deputy:deputy . .
RUN rm -rf \
    .dockerignore \
    docker \
    poetry.lock \
    pyproject.toml

USER deputy

ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
