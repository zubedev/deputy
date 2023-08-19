import os

from celery import Celery
from celery.app.task import Task
from celery.local import Proxy

# monkey patching to fix
Task.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("deputy")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)  # type: ignore[misc]
def debug_task(self: Proxy) -> None:
    print(f"Request: {self.request!r}")
