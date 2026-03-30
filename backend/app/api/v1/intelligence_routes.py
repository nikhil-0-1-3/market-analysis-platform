from fastapi import APIRouter, Query

from app.models.alert import AlertPayload, AlertResult
from app.models.intelligence import (
    BatchSignalRequest,
    BatchSignalResponse,
    ImpactAnalysis,
    LiveSignalsResponse,
    SignalRequest,
    SignalResponse,
    SourceEvent,
    WatchlistScanRequest,
    WatchlistScanResponse,
)
from app.models.product import ProductOverview
from app.services.alert_service import deliver_alert
from app.services.connector_service import (
    get_cached_live_events,
    get_connector_status,
    get_source_catalog,
    load_sample_events,
    refresh_live_events,
)
from app.services.feed_service import get_live_signals
from app.services.ingestion_service import ingest_event, ingest_events
from app.services.nlp_impact_service import analyze_impact
from app.services.product_service import get_product_overview
from app.services.signal_service import generate_signal, generate_signals_for_events, scan_watchlist

router = APIRouter(tags=["intelligence"])


@router.get("/overview", response_model=ProductOverview)
def overview() -> ProductOverview:
    return get_product_overview()


@router.get("/connectors/sources")
def connectors_sources() -> dict[str, list[str]]:
    return get_source_catalog()


@router.get("/connectors/status")
def connectors_status() -> dict[str, str | int | bool | None | dict[str, int]]:
    return get_connector_status()


@router.post("/connectors/refresh-live", response_model=list[SourceEvent])
def connectors_refresh_live(
    limit_per_source: int = Query(default=20, ge=1, le=50),
    india_only: bool = Query(default=True),
) -> list[SourceEvent]:
    return refresh_live_events(limit_per_source=limit_per_source, india_only=india_only)


@router.get("/connectors/live-events", response_model=list[SourceEvent])
def connectors_live_events(
    limit: int = Query(default=30, ge=1, le=200),
    region: str | None = Query(default=None, min_length=2, max_length=8),
) -> list[SourceEvent]:
    return get_cached_live_events(limit=limit, region=region)


@router.get("/connectors/sample-events", response_model=list[SourceEvent])
def sample_events(
    limit: int = Query(default=20, ge=1, le=200),
    region: str | None = Query(default=None, min_length=2, max_length=8),
) -> list[SourceEvent]:
    return load_sample_events(limit=limit, region=region)


@router.get("/live-signals", response_model=LiveSignalsResponse)
def live_signals(region: str = Query(default="IN", min_length=2, max_length=8)) -> LiveSignalsResponse:
    return get_live_signals(region=region)


@router.post("/analyze-event", response_model=ImpactAnalysis)
def analyze_event(payload: SourceEvent) -> ImpactAnalysis:
    event = ingest_event(payload)
    return analyze_impact(event)


@router.post("/ingest-batch", response_model=BatchSignalResponse)
def ingest_batch(payload: BatchSignalRequest) -> BatchSignalResponse:
    normalized = ingest_events(payload.events)
    return generate_signals_for_events(normalized)


@router.post("/scan-watchlist", response_model=WatchlistScanResponse)
def scan_watchlist_route(payload: WatchlistScanRequest) -> WatchlistScanResponse:
    symbols = [symbol.strip().upper() for symbol in payload.symbols if symbol.strip()]
    return scan_watchlist(symbols=symbols, region=payload.region.upper(), source=payload.source)


@router.post("/generate-signal", response_model=SignalResponse)
def generate_signal_route(payload: SignalRequest) -> SignalResponse:
    return generate_signal(payload)


@router.post("/send-alert", response_model=AlertResult)
def send_alert(payload: AlertPayload) -> AlertResult:
    return deliver_alert(payload)


@router.get("/audit/decision-log")
def decision_log() -> dict[str, list[dict[str, str]]]:
    return {
        "events": [
            {
                "id": "audit-demo-1",
                "input_hash": "sha256:demo-event",
                "decision": "watch",
                "timestamp": "2026-03-29T00:00:00Z",
                "region_policy": "IN",
            }
        ]
    }
