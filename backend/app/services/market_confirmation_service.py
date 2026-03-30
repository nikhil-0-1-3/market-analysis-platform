from app.models.intelligence import ImpactAnalysis, PriceActionSnapshot


def confirm_with_price_action(analysis: ImpactAnalysis, snapshot: PriceActionSnapshot) -> float:
    # Reduces false alerts by combining event impact and market confirmation.
    volume_score = min(1.0, snapshot.volume_spike / 3)
    volatility_penalty = min(0.25, snapshot.volatility / 10)
    trend_alignment = (snapshot.trend_score + 1) / 2

    if analysis.sentiment == "negative":
        trend_alignment = 1 - trend_alignment

    raw = (analysis.impact_strength * 0.45) + (volume_score * 0.30) + (trend_alignment * 0.25)
    return max(0.0, min(1.0, raw - volatility_penalty))
