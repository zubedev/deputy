#!/usr/bin/env python
"""Gunicorn configuration file
https://docs.gunicorn.org/en/stable/settings.html
"""
import os

# server
bind = "0.0.0.0:8000"

# logging
accesslog = "-"
errorlog = "-"

# workers
workers = os.cpu_count() + 1  # type: ignore[operator]
worker_class = "uvicorn.workers.UvicornWorker"
