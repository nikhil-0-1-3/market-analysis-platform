from celery import Celery
from app.core.config import settings

celery_app = Celery("worker", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task
def backfill_news_task(source: str) -> str:
    return f"Backfill completed for {source}"
