"""Stripe webhook handler."""

import hashlib
import hmac
from typing import Any

import stripe
from fastapi import APIRouter, Header, Request
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AuthenticationError, ValidationError
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.api_key import APIKey

router = APIRouter()
logger = get_logger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def verify_stripe_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify Stripe webhook signature.

    Args:
        payload: Raw request body
        signature: Stripe signature from header
        secret: Webhook secret

    Returns:
        True if signature is valid
    """
    try:
        # Extract timestamp and signatures
        elements = signature.split(",")
        timestamp = None
        signatures = []

        for element in elements:
            key, value = element.split("=")
            if key == "t":
                timestamp = value
            elif key.startswith("v"):
                signatures.append(value)

        if not timestamp or not signatures:
            return False

        # Compute expected signature
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        expected_sig = hmac.new(
            secret.encode(), signed_payload.encode(), hashlib.sha256
        ).hexdigest()

        # Compare signatures
        return any(hmac.compare_digest(expected_sig, sig) for sig in signatures)

    except Exception:
        return False


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
) -> dict[str, str]:
    """
    Handle Stripe webhook events.

    Processes subscription updates and updates API key plans accordingly.
    """
    # Get raw body
    body = await request.body()

    # Verify signature
    if not stripe_signature or not settings.STRIPE_WEBHOOK_SECRET:
        raise AuthenticationError(
            message="Missing webhook signature", hint="Configure STRIPE_WEBHOOK_SECRET"
        )

    if not verify_stripe_signature(body, stripe_signature, settings.STRIPE_WEBHOOK_SECRET):
        raise AuthenticationError(
            message="Invalid webhook signature", hint="Signature verification failed"
        )

    # Parse event
    try:
        event = stripe.Event.construct_from(await request.json(), stripe.api_key)
    except Exception as e:
        raise ValidationError(message=f"Invalid event data: {str(e)}")

    # Handle different event types
    logger.info(f"Received Stripe event: {event.type}")

    if event.type == "customer.subscription.created":
        await handle_subscription_created(event.data.object)
    elif event.type == "customer.subscription.updated":
        await handle_subscription_updated(event.data.object)
    elif event.type == "customer.subscription.deleted":
        await handle_subscription_deleted(event.data.object)

    return {"status": "success"}


async def handle_subscription_created(subscription: Any) -> None:
    """Handle new subscription creation."""
    customer_id = subscription.customer
    plan = determine_plan_from_subscription(subscription)

    logger.info(f"Subscription created for customer {customer_id}, plan: {plan}")

    # Update API keys for this customer
    async with AsyncSession(bind=get_db.__wrapped__()) as db:
        await db.execute(
            update(APIKey)
            .where(APIKey.stripe_customer_id == customer_id)
            .values(plan=plan, stripe_subscription_id=subscription.id)
        )
        await db.commit()


async def handle_subscription_updated(subscription: Any) -> None:
    """Handle subscription updates."""
    customer_id = subscription.customer
    plan = determine_plan_from_subscription(subscription)

    logger.info(f"Subscription updated for customer {customer_id}, plan: {plan}")

    # Update API keys
    async with AsyncSession(bind=get_db.__wrapped__()) as db:
        await db.execute(
            update(APIKey).where(APIKey.stripe_subscription_id == subscription.id).values(plan=plan)
        )
        await db.commit()


async def handle_subscription_deleted(subscription: Any) -> None:
    """Handle subscription cancellation."""
    logger.info(f"Subscription deleted: {subscription.id}")

    # Downgrade to free plan
    async with AsyncSession(bind=get_db.__wrapped__()) as db:
        await db.execute(
            update(APIKey)
            .where(APIKey.stripe_subscription_id == subscription.id)
            .values(plan="free", stripe_subscription_id=None)
        )
        await db.commit()


def determine_plan_from_subscription(subscription: Any) -> str:
    """
    Determine plan tier from Stripe subscription.

    Args:
        subscription: Stripe subscription object

    Returns:
        Plan name (free, pro, or enterprise)
    """
    # Check product ID
    if subscription.items and len(subscription.items.data) > 0:
        product_id = subscription.items.data[0].price.product

        if product_id == settings.STRIPE_PRODUCT_PRO:
            return "pro"
        elif product_id == settings.STRIPE_PRODUCT_ENTERPRISE:
            return "enterprise"

    return "free"
