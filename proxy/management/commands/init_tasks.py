from typing import Any

from django.core.management import BaseCommand
from django_celery_beat.models import CrontabSchedule, IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Initialize celery beats scheduler and tasks"

    def handle(self, *args: Any, **options: Any) -> None:
        # First, create the interval schedules for certain periods
        IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)
        IntervalSchedule.objects.get_or_create(every=15, period=IntervalSchedule.MINUTES)
        IntervalSchedule.objects.get_or_create(every=30, period=IntervalSchedule.MINUTES)
        IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.HOURS)

        # Then, create the crontab schedules for certain times
        params = {"hour": "*", "day_of_week": "*", "day_of_month": "*", "month_of_year": "*"}
        CrontabSchedule.objects.get_or_create(minute="*/5", **params)  # every 5 minutes
        CrontabSchedule.objects.get_or_create(minute="*/15", **params)  # every 15 minutes
        CrontabSchedule.objects.get_or_create(minute="*/30", **params)  # every 30 minutes
        CrontabSchedule.objects.get_or_create(minute="0", **params)  # every hour
        CrontabSchedule.objects.get_or_create(minute="15", **params)  # every hour on the 15th minute
        CrontabSchedule.objects.get_or_create(minute="30", **params)  # every hour on the 30th minute
        CrontabSchedule.objects.get_or_create(minute="45", **params)  # every hour on the 45th minute

        # Finally, create schedules for the tasks
        crontab, _ = CrontabSchedule.objects.get_or_create(minute="5", **params)  # every hour on the 5th minute
        PeriodicTask.objects.get_or_create(
            name="proxy.tasks.crawl_workflow", defaults={"task": "proxy.tasks.crawl_workflow", "crontab": crontab}
        )
