import os

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.services.connector_service import refresh_live_events

scheduler = BackgroundScheduler(timezone="UTC")


def _refresh_live_data_job() -> None:
    refresh_live_events(limit_per_source=settings.connectors_default_limit, india_only=settings.connectors_india_only)


def schedule_jobs() -> None:
    if scheduler.running:
        return

    if os.getenv("PYTEST_CURRENT_TEST"):
        return

    _refresh_live_data_job()
    scheduler.add_job(
        _refresh_live_data_job,
        "interval",
        minutes=max(1, settings.connectors_refresh_minutes),
        id="live-data-refresh",
        replace_existing=True,
    )
    scheduler.start()


def shutdown_jobs() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
