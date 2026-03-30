from datetime import datetime
from pydantic import BaseModel, Field


class MarketSignalRequest(BaseModel):
    symbol: str = Field(..., examples=["NSE:RELIANCE"])
    interval: str = Field(default="15m", examples=["1m", "5m", "15m", "1h"])


class MarketSignalResponse(BaseModel):
    symbol: str
    confidence: float
    direction: str
    reason: str
    generated_at: datetime
