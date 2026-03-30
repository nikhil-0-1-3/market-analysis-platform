from pydantic import BaseModel, Field


class AlertPayload(BaseModel):
    channel: str = Field(..., examples=["telegram", "email", "webhook"])
    recipient: str
    title: str
    message: str
    metadata: dict[str, str] = Field(default_factory=dict)


class AlertResult(BaseModel):
    delivered: bool
    channel: str
    recipient: str
    tracking_id: str
