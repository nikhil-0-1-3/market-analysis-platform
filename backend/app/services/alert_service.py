from uuid import uuid4

from app.models.alert import AlertPayload, AlertResult


def deliver_alert(payload: AlertPayload) -> AlertResult:
    # Delivery integrations (Telegram/email/webhooks) would be plugged here.
    return AlertResult(
        delivered=True,
        channel=payload.channel,
        recipient=payload.recipient,
        tracking_id=f"alrt-{uuid4().hex[:12]}",
    )
