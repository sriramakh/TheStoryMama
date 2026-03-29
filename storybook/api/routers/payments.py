"""FastSpring payment webhook router."""

import hmac
import hashlib
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from config import Config

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

logger = logging.getLogger(__name__)

# Product path → credits mapping
PRODUCT_CREDITS = {
    "story-pack-5": {"credits": 5, "type": "one-time"},
    "monthly-10": {"credits": 10, "type": "subscription"},
    "annual-15": {"credits": 15, "type": "subscription"},
}

# In-memory credit store (for now — replace with DB later)
# user_email -> {"credits": int, "orders": list}
user_credits: dict[str, dict] = {}


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify FastSpring webhook HMAC-SHA256 signature."""
    secret = Config.FASTSPRING_WEBHOOK_SECRET
    if not secret:
        logger.warning("No webhook secret configured — skipping verification")
        return True

    expected = hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@router.post("/fastspring-webhook")
async def fastspring_webhook(request: Request):
    """Handle FastSpring webhook events."""
    payload = await request.body()

    # Verify signature (log but don't block for now — fixing HMAC format)
    signature = request.headers.get("X-FS-Signature", "")
    if signature:
        is_valid = verify_webhook_signature(payload, signature)
        logger.info(f"Webhook signature valid: {is_valid}")
    else:
        logger.info("No X-FS-Signature header — processing anyway")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    events = data.get("events", [])
    logger.info(f"Webhook payload keys: {list(data.keys())}, events: {len(events)}")

    for event in events:
        event_type = event.get("type", "")
        event_data = event.get("data", {})

        logger.info(f"FastSpring event: {event_type}")

        if event_type == "order.completed":
            _handle_order_completed(event_data)
        elif event_type == "subscription.activated":
            _handle_subscription_activated(event_data)
        elif event_type == "subscription.deactivated":
            _handle_subscription_deactivated(event_data)
        elif event_type == "subscription.charge.completed":
            _handle_subscription_renewed(event_data)

    return {"received": True}


def _handle_order_completed(data: dict):
    """Grant credits when a one-time order completes."""
    logger.info(f"Order data keys: {list(data.keys())}")

    # FastSpring sends email in various places depending on event type
    email = ""
    # Try nested account.contact.email
    account = data.get("account", {})
    if isinstance(account, dict):
        contact = account.get("contact", {})
        if isinstance(contact, dict):
            email = contact.get("email", "")
        email = email or account.get("email", "")

    # Try top-level recipient/customer
    if not email:
        recipient = data.get("recipient", {})
        if isinstance(recipient, dict):
            email = recipient.get("email", "")
    if not email:
        customer = data.get("customer", {})
        if isinstance(customer, dict):
            email = customer.get("email", "")
    if not email:
        # Try tags or reference
        tags = data.get("tags", {})
        if isinstance(tags, dict):
            email = tags.get("email", "")

    logger.info(f"Extracted email: {email}")

    items = data.get("items", [])
    if not isinstance(items, list):
        items = []
    order_id = data.get("id", data.get("reference", ""))

    for item in items:
        # FastSpring may use "product" as string or nested object
        product_path = item.get("product", "")
        if isinstance(product_path, dict):
            product_path = product_path.get("path", "") or product_path.get("product", "")

        # Also check "productPath" or "path"
        if not product_path:
            product_path = item.get("productPath", "") or item.get("path", "")

        logger.info(f"Item product_path: {product_path}, item keys: {list(item.keys())}")

        product_config = PRODUCT_CREDITS.get(product_path)

        if not product_config:
            logger.warning(f"Unknown product: {product_path}")
            continue

        credits = product_config["credits"]

        if not email:
            email = "unknown@email.com"

        if email not in user_credits:
            user_credits[email] = {"credits": 0, "orders": []}

        user_credits[email]["credits"] += credits
        user_credits[email]["orders"].append({
            "order_id": order_id,
            "product": product_path,
            "credits": credits,
            "type": product_config["type"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        logger.info(f"Granted {credits} credits to {email} (order: {order_id}, product: {product_path})")


def _handle_subscription_activated(data: dict):
    """Grant credits when a subscription starts."""
    email = data.get("account", {}).get("contact", {}).get("email", "")
    if not email:
        return

    product_path = data.get("product", {}).get("product", "")
    product_config = PRODUCT_CREDITS.get(product_path)

    if not product_config:
        # Try extracting from instructions or items
        for key in ["instructions", "items"]:
            items = data.get(key, [])
            if isinstance(items, list):
                for item in items:
                    pp = item.get("product", "")
                    if pp in PRODUCT_CREDITS:
                        product_config = PRODUCT_CREDITS[pp]
                        product_path = pp
                        break

    if not product_config:
        logger.warning(f"Unknown subscription product for {email}")
        return

    credits = product_config["credits"]
    sub_id = data.get("id", "")

    if email not in user_credits:
        user_credits[email] = {"credits": 0, "orders": []}

    user_credits[email]["credits"] += credits
    user_credits[email]["orders"].append({
        "subscription_id": sub_id,
        "product": product_path,
        "credits": credits,
        "type": "subscription_start",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    logger.info(f"Subscription activated: {credits} credits to {email} (sub: {sub_id})")


def _handle_subscription_deactivated(data: dict):
    """Handle subscription cancellation."""
    email = data.get("account", {}).get("contact", {}).get("email", "")
    sub_id = data.get("id", "")
    logger.info(f"Subscription deactivated for {email} (sub: {sub_id})")


def _handle_subscription_renewed(data: dict):
    """Grant credits on subscription renewal."""
    email = data.get("account", {}).get("contact", {}).get("email", "")
    if not email:
        return

    product_path = data.get("product", {}).get("product", "")
    product_config = PRODUCT_CREDITS.get(product_path)

    if not product_config:
        logger.warning(f"Unknown renewal product for {email}")
        return

    credits = product_config["credits"]

    if email not in user_credits:
        user_credits[email] = {"credits": 0, "orders": []}

    user_credits[email]["credits"] += credits
    user_credits[email]["orders"].append({
        "product": product_path,
        "credits": credits,
        "type": "renewal",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    logger.info(f"Subscription renewed: {credits} credits to {email}")


@router.get("/credits/{email}")
def get_user_credits(email: str):
    """Get credit balance for a user."""
    data = user_credits.get(email, {"credits": 0, "orders": []})
    return {
        "email": email,
        "credits": data["credits"],
        "orders": data["orders"],
    }
