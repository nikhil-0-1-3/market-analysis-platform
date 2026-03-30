def build_risk_warning(confidence_score: float, horizon: str) -> str:
    if confidence_score < 0.5:
        return "Low conviction: treat as watchlist-only, avoid leverage."
    if horizon == "intraday":
        return "Intraday risk: use tight stop-loss and position limits."
    return "Swing risk: watch overnight gaps and event reversals."
