from app.models.intelligence import LiveSignalsResponse
from app.services.connector_service import get_cached_live_events
from app.services.signal_service import generate_signals_for_events


def get_live_signals(region: str = "IN") -> LiveSignalsResponse:
    events = get_cached_live_events(limit=30, region=region)
    batch = generate_signals_for_events(events)
    return LiveSignalsResponse(region=region.upper(), signals=batch.signals)
