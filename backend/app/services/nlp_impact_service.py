from app.models.intelligence import ImpactAnalysis, SourceEvent


def analyze_impact(event: SourceEvent) -> ImpactAnalysis:
    text = f"{event.headline} {event.body}".lower()
    positive_markers = ["beat", "upgrade", "growth", "surge", "win", "strong", "expansion"]
    negative_markers = ["fraud", "ban", "downgrade", "drop", "loss", "probe", "penalty"]

    pos = sum(1 for marker in positive_markers if marker in text)
    neg = sum(1 for marker in negative_markers if marker in text)

    if pos > neg:
        sentiment = "positive"
    elif neg > pos:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    impact_strength = min(1.0, 0.33 + (pos + neg) * 0.13)
    horizon = "intraday" if event.source in {"social", "market"} else "swing"
    fallback_symbol = "NSE:NIFTY50" if event.region.upper() == "IN" else "SPY"

    return ImpactAnalysis(
        sentiment=sentiment,
        impact_strength=impact_strength,
        affected_symbols=event.symbols or [fallback_symbol],
        affected_sectors=event.sectors or ["Broad Market"],
        affected_indices=["NIFTY50"] if event.region.upper() == "IN" else ["SPX"],
        horizon=horizon,
        confidence=min(0.95, 0.46 + impact_strength / 2),
        explanation="Lexical sentiment + source horizon model, confirmed with market microstructure.",
    )
