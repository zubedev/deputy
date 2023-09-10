```text
██████╗ ███████╗██████╗ ██╗   ██╗████████╗██╗   ██╗
██╔══██╗██╔════╝██╔══██╗██║   ██║╚══██╔══╝╚██╗ ██╔╝
██║  ██║█████╗  ██████╔╝██║   ██║   ██║    ╚████╔╝
██║  ██║██╔══╝  ██╔═══╝ ██║   ██║   ██║     ╚██╔╝
██████╔╝███████╗██║     ╚██████╔╝   ██║      ██║
╚═════╝ ╚══════╝╚═╝      ╚═════╝    ╚═╝      ╚═╝
>----------------------------- REST API for Proxies
```
[![django](https://img.shields.io/badge/django-4.2-%23092E20?style=flat-square&logo=django)](https://www.djangoproject.com)
[![python](https://img.shields.io/badge/python-3.11-%233776AB?style=flat-square&logo=python)](https://www.python.org)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org)
[![black](https://img.shields.io/badge/code%20style-black-black.svg?style=flat-square&logo=stylelint)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit)](https://pre-commit.com)
[![license](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/zubedev/deputy/actions/workflows/ci.yml/badge.svg)](https://github.com/zubedev/deputy/actions/workflows/ci.yml)

## Features

- [x] Rest API providing free proxies to use
- [x] Integration with [scrapydoo](https://github.com/zubedev/scrapydoo) to obtain proxies
- [x] Integration with [inspector](https://github.com/zubedev/inspector) to validate proxies
- [x] Proxies updated and checked hourly

## Usage

```bash
# Copy the example environment file to .env
# SCRAPYD_URL must be set for the workflow to work,
# You can get an instance up and running through https://github.com/zubedev/scrapydoo
cp .env.example .env

# Build the docker image and run the container
docker-compose up --build --detach

# You can scale up the number of workers for more concurrency
docker-compose up --scale worker=4 --detach
```

[Deputy API](http://localhost:8000) is now available at http://localhost:8000. If `DEBUG=True`, you can see the browsable API.

[Deputy Admin](http://localhost:8000/admin) is now available at http://localhost:8000/admin. Credentials are set automatically from `.env` file.

## Endpoints

- [random](http://localhost:8000/proxies/random): `/proxies/random` - get a random proxy

## Development

```bash
# Poetry is required for installing and managing dependencies
# https://python-poetry.org/docs/#installation
poetry install

# If you don't like doing `poetry run` all the time
# poetry shell  # Activate virtual environment in terminal

# Requires a PostgreSQL database to be running and configured in .env
# poetry run python manage.py makemigrations  # Create migrations
poetry run python manage.py migrate  # Run migrations

# Collect static files for whitenoise
poetry run python manage.py collectstatic

# Run Deputy API
poetry run python manage.py runserver 0.0.0.0:8000

# Create a superuser
poetry run python manage.py createsuperuser

# Install pre-commit hooks
poetry run pre-commit install

# Formatting (inplace formats code)
poetry run black .

# Linting (and to fix automatically)
poetry run ruff .
poetry run ruff --fix .

# Type checking
poetry run mypy .
```

Configuration details can be found in [pyproject.toml](pyproject.toml).

## Support
[![Paypal](https://img.shields.io/badge/Paypal-@MdZubairBeg-253B80?&logo=paypal)](https://paypal.me/MdZubairBeg/10)
