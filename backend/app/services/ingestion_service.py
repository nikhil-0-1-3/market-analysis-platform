from app.models.intelligence import SourceEvent


def normalize_event(event: SourceEvent) -> SourceEvent:
    symbols = [s.strip().upper() for s in event.symbols if s.strip()]
    sectors = [s.strip().title() for s in event.sectors if s.strip()]
    region = event.region.strip().upper() if event.region.strip() else "IN"
    return SourceEvent(
        source=event.source,
        headline=event.headline.strip(),
        body=event.body.strip(),
        symbols=symbols,
        sectors=sectors,
        region=region,
        occurred_at=event.occurred_at,
    )


def ingest_event(event: SourceEvent) -> SourceEvent:
    return normalize_event(event)


def ingest_events(events: list[SourceEvent]) -> list[SourceEvent]:
    normalized = [normalize_event(event) for event in events]
    dedup: dict[str, SourceEvent] = {}
    for event in normalized:
        key = f"{event.source}|{event.region}|{event.headline.lower()}"
        dedup[key] = event
    return list(dedup.values())
