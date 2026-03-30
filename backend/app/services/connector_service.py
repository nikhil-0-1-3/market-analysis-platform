import html
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

import httpx

from app.core.config import settings
from app.models.intelligence import SourceEvent


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "sample_events.json"

NEWS_RSS_SOURCES: list[tuple[str, str]] = [
    ("economic_times_markets", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
    ("moneycontrol_business", "https://www.moneycontrol.com/rss/business.xml"),
    ("business_standard_markets", "https://www.business-standard.com/rss/markets-106.rss"),
    ("mint_markets", "https://www.livemint.com/rss/markets"),
    ("the_hindu_business", "https://www.thehindu.com/business/feeder/default.rss"),
]

REDDIT_SOURCES: list[tuple[str, str]] = [
    ("reddit_indianstreetbets", "https://www.reddit.com/r/IndianStreetBets/hot.json?limit=40"),
    ("reddit_indiainvestments", "https://www.reddit.com/r/IndiaInvestments/hot.json?limit=40"),
    ("reddit_stocks", "https://www.reddit.com/r/stocks/hot.json?limit=40"),
]

X_FALLBACK_RSS = "https://nitter.net/search/rss?f=tweets&q={query}"

_KEYWORD_SYMBOLS: dict[str, list[str]] = {
    "nifty": ["NSE:NIFTY50"],
    "sensex": ["BSE:SENSEX"],
    "bank nifty": ["NSE:BANKNIFTY"],
    "bank": ["NSE:BANKNIFTY"],
    "it": ["NSE:NIFTYIT"],
    "reliance": ["NSE:RELIANCE"],
    "hdfc": ["NSE:HDFCBANK"],
    "icici": ["NSE:ICICIBANK"],
    "infosys": ["NSE:INFY"],
    "tcs": ["NSE:TCS"],
    "wipro": ["NSE:WIPRO"],
    "lt": ["NSE:LT"],
    "adani": ["NSE:ADANIENT"],
    "rbi": ["NSE:BANKNIFTY"],
}

_LIVE_CACHE: list[SourceEvent] = []
_LAST_REFRESH_AT: datetime | None = None
_LAST_ERROR: str | None = None
_LAST_COUNTS: dict[str, int] = {}
_LAST_X_MODE: str = "disabled"
_CACHE_LOCK = Lock()


def load_sample_events(limit: int = 20, region: str | None = None) -> list[SourceEvent]:
    if not DATA_FILE.exists():
        return []

    raw = json.loads(DATA_FILE.read_text(encoding="utf-8-sig"))
    events = [SourceEvent(**item) for item in raw]

    if region:
        events = [event for event in events if event.region.upper() == region.upper()]

    return events[: max(1, min(limit, 200))]


def _strip_html(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value or "")
    return html.unescape(re.sub(r"\s+", " ", without_tags)).strip()


def _guess_region(text: str) -> str:
    t = text.lower()
    if any(token in t for token in ["india", "indian", "nse", "bse", "nifty", "sensex", "rbi", "rupee", "sebi"]):
        return "IN"
    return "US"


def _infer_symbols(text: str) -> list[str]:
    t = text.lower()
    symbols: list[str] = []
    for key, mapped in _KEYWORD_SYMBOLS.items():
        if key in t:
            symbols.extend(mapped)

    if not symbols:
        return ["NSE:NIFTY50"] if _guess_region(t) == "IN" else ["NYSE:SPY"]

    return list(dict.fromkeys(symbols))


def _infer_sectors(text: str) -> list[str]:
    t = text.lower()
    sectors: list[str] = []
    if "bank" in t or "rbi" in t:
        sectors.append("Banking")
    if "it" in t or "software" in t or "tech" in t:
        sectors.append("IT")
    if "infra" in t or "rail" in t or "construction" in t:
        sectors.append("Infrastructure")
    if "oil" in t or "energy" in t or "gas" in t:
        sectors.append("Energy")
    if "auto" in t:
        sectors.append("Auto")
    if not sectors:
        sectors.append("Broad Market")
    return sectors


def _event_from_text(*, source: str, provider: str, headline: str, body: str, source_url: str | None, source_id: str | None, engagement_score: float = 0.0) -> SourceEvent:
    h = _strip_html(headline)
    b = _strip_html(body)
    text = f"{h} {b}"

    return SourceEvent(
        source=source,
        provider=provider,
        source_url=source_url,
        source_id=source_id,
        language="en",
        engagement_score=max(0.0, engagement_score),
        headline=h or f"{provider} update",
        body=b,
        symbols=_infer_symbols(text),
        sectors=_infer_sectors(text),
        region=_guess_region(text),
        occurred_at=datetime.now(UTC),
    )


def _fetch_rss_events(provider: str, url: str, limit: int) -> list[SourceEvent]:
    with httpx.Client(timeout=8.0, follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": "ai-market-intelligence-bot/1.0"})
    response.raise_for_status()

    root = ET.fromstring(response.text)
    items = root.findall(".//item")

    events: list[SourceEvent] = []
    for item in items[:limit]:
        title = item.findtext("title") or f"{provider} market update"
        description = item.findtext("description") or ""
        link = item.findtext("link")
        guid = item.findtext("guid")
        events.append(_event_from_text(source="news", provider=provider, headline=title, body=description, source_url=link, source_id=guid))
    return events


def _fetch_reddit_events(provider: str, url: str, limit: int) -> list[SourceEvent]:
    with httpx.Client(timeout=8.0, follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": "ai-market-intelligence-bot/1.0"})
    response.raise_for_status()

    payload = response.json()
    children = payload.get("data", {}).get("children", [])

    events: list[SourceEvent] = []
    for row in children[:limit]:
        data = row.get("data", {})
        title = data.get("title", f"{provider} social trend")
        body = data.get("selftext", "")
        permalink = data.get("permalink", "")
        score = float(max(0, data.get("score", 0)))
        events.append(_event_from_text(source="social", provider=provider, headline=title, body=body, source_url=f"https://www.reddit.com{permalink}" if permalink else None, source_id=data.get("id"), engagement_score=score))
    return events


def _fetch_x_api_events(limit: int) -> list[SourceEvent]:
    if not settings.x_bearer_token:
        return []

    url = "https://api.x.com/2/tweets/search/recent"
    params = {
        "query": settings.x_query,
        "max_results": max(10, min(100, limit)),
        "tweet.fields": "created_at,lang,public_metrics",
    }

    with httpx.Client(timeout=8.0, follow_redirects=True) as client:
        response = client.get(url, params=params, headers={"Authorization": f"Bearer {settings.x_bearer_token}"})
    response.raise_for_status()

    payload = response.json()
    rows = payload.get("data", [])

    events: list[SourceEvent] = []
    for row in rows[:limit]:
        text = row.get("text", "X market trend")
        metrics = row.get("public_metrics") or {}
        engagement = float(metrics.get("retweet_count", 0) + metrics.get("reply_count", 0) + metrics.get("like_count", 0))
        events.append(_event_from_text(source="social", provider="x_recent_search", headline=text, body="", source_url=f"https://x.com/i/web/status/{row.get('id')}", source_id=row.get("id"), engagement_score=engagement))
    return events


def _fetch_x_fallback_rss(limit: int) -> list[SourceEvent]:
    query = quote_plus("NSE OR BSE OR NIFTY OR SENSEX OR RBI OR Indian stocks")
    url = X_FALLBACK_RSS.format(query=query)
    try:
        return _fetch_rss_events("x_fallback_rss", url, limit)
    except (ET.ParseError, ValueError):
        return []


def _fetch_x_events(limit: int) -> tuple[list[SourceEvent], str]:
    if not settings.x_bearer_token:
        events = _fetch_x_fallback_rss(limit)
        return events, "fallback_rss" if events else "fallback_unavailable"

    try:
        return _fetch_x_api_events(limit), "official_api"
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in {401, 402, 403, 429}:
            events = _fetch_x_fallback_rss(limit)
            return events, "fallback_rss" if events else "fallback_unavailable"
        raise


def _dedupe_events(events: list[SourceEvent]) -> list[SourceEvent]:
    dedup: dict[str, SourceEvent] = {}
    for event in events:
        key = f"{event.provider}|{event.source}|{event.region}|{event.headline.lower()}"
        dedup[key] = event
    return list(dedup.values())


def refresh_live_events(limit_per_source: int = 20, india_only: bool | None = None) -> list[SourceEvent]:
    global _LAST_REFRESH_AT, _LAST_ERROR, _LAST_COUNTS, _LAST_X_MODE

    if india_only is None:
        india_only = settings.connectors_india_only

    collected: list[SourceEvent] = []
    errors: list[str] = []
    counts: dict[str, int] = {}

    for provider, url in NEWS_RSS_SOURCES:
        try:
            events = _fetch_rss_events(provider, url, limit=max(5, min(limit_per_source, 50)))
            counts[provider] = len(events)
            collected.extend(events)
        except Exception as exc:
            counts[provider] = 0
            errors.append(f"{provider}:{exc}")

    for provider, url in REDDIT_SOURCES:
        try:
            events = _fetch_reddit_events(provider, url, limit=max(5, min(limit_per_source, 50)))
            counts[provider] = len(events)
            collected.extend(events)
        except Exception as exc:
            counts[provider] = 0
            errors.append(f"{provider}:{exc}")

    try:
        x_events, x_mode = _fetch_x_events(limit=max(5, min(limit_per_source, 50)))
        _LAST_X_MODE = x_mode
        counts["x_recent_search"] = len(x_events)
        collected.extend(x_events)
    except Exception as exc:
        _LAST_X_MODE = "error"
        counts["x_recent_search"] = 0
        errors.append(f"x_recent_search:{exc}")

    deduped = _dedupe_events(collected)
    if india_only:
        deduped = [event for event in deduped if event.region.upper() == "IN"]

    if not deduped:
        deduped = load_sample_events(limit=60, region="IN" if india_only else None)

    with _CACHE_LOCK:
        _LIVE_CACHE.clear()
        _LIVE_CACHE.extend(deduped)
        _LAST_REFRESH_AT = datetime.now(UTC)
        _LAST_ERROR = " | ".join(errors) if errors else None
        _LAST_COUNTS = counts

    return deduped


def get_cached_live_events(limit: int = 40, region: str | None = None) -> list[SourceEvent]:
    with _CACHE_LOCK:
        if not _LIVE_CACHE:
            _LIVE_CACHE.extend(load_sample_events(limit=60, region="IN"))
        events = list(_LIVE_CACHE)

    if region:
        events = [event for event in events if event.region.upper() == region.upper()]

    return events[: max(1, min(limit, 200))]


def get_connector_status() -> dict[str, str | int | bool | None | dict[str, int]]:
    with _CACHE_LOCK:
        cached = len(_LIVE_CACHE)
        refreshed = _LAST_REFRESH_AT.isoformat() if _LAST_REFRESH_AT else None
        error = _LAST_ERROR
        counts = dict(_LAST_COUNTS)
        x_mode = _LAST_X_MODE

    return {
        "cached_events": cached,
        "last_refresh_at": refreshed,
        "last_error": error,
        "news_sources": len(NEWS_RSS_SOURCES),
        "social_sources": len(REDDIT_SOURCES) + 1,
        "x_enabled": bool(settings.x_bearer_token),
        "x_mode": x_mode,
        "provider_counts": counts,
    }


def get_source_catalog() -> dict[str, list[str]]:
    return {
        "news": [name for name, _ in NEWS_RSS_SOURCES],
        "social": [name for name, _ in REDDIT_SOURCES] + ["x_recent_search"],
    }


with _CACHE_LOCK:
    _LIVE_CACHE.extend(load_sample_events(limit=40, region="IN"))
