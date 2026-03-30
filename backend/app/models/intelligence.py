from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class SourceEvent(BaseModel):
    source: Literal["news", "social", "market"]
    provider: str | None = None
    source_url: str | None = None
    source_id: str | None = None
    language: str = "en"
    engagement_score: float = Field(default=0.0, ge=0.0)
    headline: str = Field(..., min_length=3)
    body: str = ""
    symbols: list[str] = Field(default_factory=list)
    sectors: list[str] = Field(default_factory=list)
    region: str = "IN"
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ImpactAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    impact_strength: float = Field(..., ge=0.0, le=1.0)
    affected_symbols: list[str]
    affected_sectors: list[str]
    affected_indices: list[str]
    horizon: Literal["intraday", "swing"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str


class PriceActionSnapshot(BaseModel):
    symbol: str
    volume_spike: float = Field(..., ge=0.0)
    volatility: float = Field(..., ge=0.0)
    trend_score: float = Field(..., ge=-1.0, le=1.0)


class SignalRequest(BaseModel):
    event: SourceEvent
    price_action: PriceActionSnapshot


class SignalResponse(BaseModel):
    symbol: str
    what_happened: str
    may_move: str
    direction: Literal["buy_bias", "sell_bias", "watch"]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    risk_warning: str
    horizon: Literal["intraday", "swing"]
    audit_id: str


class LiveSignalsResponse(BaseModel):
    region: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    signals: list[SignalResponse]


class BatchSignalRequest(BaseModel):
    events: list[SourceEvent] = Field(..., min_length=1, max_length=200)


class BatchSignalResponse(BaseModel):
    count: int
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    signals: list[SignalResponse]


class WatchlistScanRequest(BaseModel):
    symbols: list[str] = Field(..., min_length=1, max_length=200)
    region: str = "IN"
    source: Literal["news", "social", "market"] = "market"


class WatchlistScanResponse(BaseModel):
    region: str
    count: int
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    signals: list[SignalResponse]
