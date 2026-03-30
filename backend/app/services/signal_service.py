from uuid import uuid4

from app.models.intelligence import (
    BatchSignalResponse,
    PriceActionSnapshot,
    SignalRequest,
    SignalResponse,
    SourceEvent,
    WatchlistScanResponse,
)
from app.services.market_confirmation_service import confirm_with_price_action
from app.services.nlp_impact_service import analyze_impact
from app.services.risk_service import build_risk_warning


def _default_price_action(symbol: str, source: str) -> PriceActionSnapshot:
    if source == "social":
        return PriceActionSnapshot(symbol=symbol, volume_spike=1.9, volatility=1.6, trend_score=0.35)
    if source == "news":
        return PriceActionSnapshot(symbol=symbol, volume_spike=2.2, volatility=1.4, trend_score=0.52)
    return PriceActionSnapshot(symbol=symbol, volume_spike=1.6, volatility=1.2, trend_score=0.44)


def generate_signal(payload: SignalRequest) -> SignalResponse:
    analysis = analyze_impact(payload.event)
    confidence = confirm_with_price_action(analysis, payload.price_action)

    if confidence >= 0.68:
        direction = "buy_bias" if analysis.sentiment == "positive" else "sell_bias"
    else:
        direction = "watch"

    may_move = ", ".join(analysis.affected_symbols or [payload.price_action.symbol])

    return SignalResponse(
        symbol=payload.price_action.symbol,
        what_happened=payload.event.headline,
        may_move=may_move,
        direction=direction,
        confidence_score=round(confidence, 3),
        risk_warning=build_risk_warning(confidence, analysis.horizon),
        horizon=analysis.horizon,
        audit_id=f"audit-{uuid4().hex[:14]}",
    )


def generate_signals_for_events(events: list[SourceEvent]) -> BatchSignalResponse:
    signals: list[SignalResponse] = []
    for event in events:
        symbol = event.symbols[0] if event.symbols else ("NSE:NIFTY50" if event.region == "IN" else "NYSE:SPY")
        signal = generate_signal(SignalRequest(event=event, price_action=_default_price_action(symbol, event.source)))
        signals.append(signal)
    return BatchSignalResponse(count=len(signals), signals=signals)


def scan_watchlist(symbols: list[str], region: str = "IN", source: str = "market") -> WatchlistScanResponse:
    events = [
        SourceEvent(
            source=source,
            headline=f"Watchlist scanner detected meaningful momentum setup on {symbol}",
            body="Automated pre-trade intelligence scan generated this candidate.",
            symbols=[symbol],
            sectors=["Watchlist"],
            region=region,
        )
        for symbol in symbols
    ]

    batch = generate_signals_for_events(events)
    return WatchlistScanResponse(region=region, count=batch.count, signals=batch.signals)
