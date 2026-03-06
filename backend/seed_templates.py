"""
Seed webhook templates into the database.
"""
import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models.webhook_template import WebhookTemplate


async def seed_templates():
    """Seed pre-configured webhook templates."""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        templates = [
            WebhookTemplate(
                id=uuid.uuid4(),
                name="Stripe Payment Events",
                provider_name="stripe",
                description="Pre-configured template for Stripe payment webhooks",
                example_payload={
                    "id": "evt_1234567890",
                    "object": "event",
                    "type": "payment_intent.succeeded",
                    "data": {
                        "object": {
                            "id": "pi_1234567890",
                            "amount": 2000,
                            "currency": "usd",
                            "status": "succeeded"
                        }
                    }
                },
                signature_algorithm="hmac-sha256",
                headers_template={
                    "Stripe-Signature": "t=<timestamp>,v1=<signature>"
                },
                category="payment"
            ),
            WebhookTemplate(
                id=uuid.uuid4(),
                name="GitHub Push Events",
                provider_name="github",
                description="Pre-configured template for GitHub push webhooks",
                example_payload={
                    "ref": "refs/heads/main",
                    "before": "abc123",
                    "after": "def456",
                    "repository": {
                        "id": 123456,
                        "name": "my-repo",
                        "full_name": "user/my-repo"
                    },
                    "pusher": {
                        "name": "user",
                        "email": "user@example.com"
                    }
                },
                signature_algorithm="hmac-sha256",
                headers_template={
                    "X-Hub-Signature-256": "sha256=<signature>"
                },
                category="vcs"
            ),
            WebhookTemplate(
                id=uuid.uuid4(),
                name="Slack Message Events",
                provider_name="slack",
                description="Pre-configured template for Slack event webhooks",
                example_payload={
                    "token": "verification_token",
                    "team_id": "T123456",
                    "event": {
                        "type": "message",
                        "channel": "C123456",
                        "user": "U123456",
                        "text": "Hello world",
                        "ts": "1234567890.123456"
                    }
                },
                signature_algorithm="hmac-sha256",
                headers_template={
                    "X-Slack-Request-Timestamp": "<timestamp>",
                    "X-Slack-Signature": "v0=<signature>"
                },
                category="messaging"
            ),
            WebhookTemplate(
                id=uuid.uuid4(),
                name="Twilio SMS Events",
                provider_name="twilio",
                description="Pre-configured template for Twilio SMS webhooks",
                example_payload={
                    "MessageSid": "SM[PLACEHOLDER_MESSAGE_SID]",
                    "AccountSid": "AC[PLACEHOLDER_ACCOUNT_SID]",
                    "From": "+1234567890",
                    "To": "+0987654321",
                    "Body": "Hello from Twilio",
                    "NumMedia": "0"
                },
                signature_algorithm="hmac-sha1",
                headers_template={
                    "X-Twilio-Signature": "<signature>"
                },
                category="messaging"
            ),
            WebhookTemplate(
                id=uuid.uuid4(),
                name="PayPal IPN Events",
                provider_name="paypal",
                description="Pre-configured template for PayPal IPN webhooks",
                example_payload={
                    "mc_gross": "19.95",
                    "invoice": "abc123",
                    "protection_eligibility": "Eligible",
                    "address_status": "confirmed",
                    "payer_id": "LPLWNMTBWAMXC",
                    "address_street": "123 Main St",
                    "payment_date": "14:30:00 Jan 01, 2024 PST",
                    "payment_status": "Completed",
                    "txn_id": "61E67681CH3238416"
                },
                signature_algorithm="hmac-sha256",
                headers_template={},
                category="payment"
            ),
        ]
        
        # Add all templates
        for template in templates:
            session.add(template)
        
        await session.commit()
        print(f"✓ Seeded {len(templates)} webhook templates")


if __name__ == "__main__":
    asyncio.run(seed_templates())
