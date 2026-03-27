"""Stripe payment and webhook router."""

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import Config
from api.db.engine import get_db
from api.db.models import User, Order, Credit
from api.middleware.auth import require_auth

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

PLAN_CONFIG = {
    "pack_5": {"credits": 5, "amount_cents": 999, "expires": False},
    "monthly_10": {"credits": 10, "amount_cents": 1299, "expires": True},
    "yearly_15": {"credits": 15, "amount_cents": 9900, "expires": True},
}


class CreateCheckoutRequest(BaseModel):
    plan_type: str
    success_url: str
    cancel_url: str


@router.post("/create-checkout")
def create_checkout(
    req: CreateCheckoutRequest,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout Session."""
    if not Config.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system not configured",
        )

    if req.plan_type not in PLAN_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan type: {req.plan_type}",
        )

    stripe.api_key = Config.STRIPE_SECRET_KEY
    plan = PLAN_CONFIG[req.plan_type]

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"TheStoryMama - {req.plan_type.replace('_', ' ').title()}",
                            "description": f"{plan['credits']} story credits",
                        },
                        "unit_amount": plan["amount_cents"],
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            metadata={
                "user_id": str(user.id),
                "plan_type": req.plan_type,
            },
        )

        # Create pending order
        order = Order(
            user_id=user.id,
            stripe_session_id=session.id,
            plan_type=req.plan_type,
            amount_cents=plan["amount_cents"],
            status="pending",
        )
        db.add(order)
        db.commit()

        return {"checkout_url": session.url}

    except stripe.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Stripe error: {str(e)}",
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    if not Config.STRIPE_SECRET_KEY or not Config.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured",
        )

    stripe.api_key = Config.STRIPE_SECRET_KEY
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.SignatureVerificationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        _handle_checkout_completed(session, db)

    return {"received": True}


def _handle_checkout_completed(session: dict, db: Session):
    """Grant credits after successful checkout."""
    user_id = session.get("metadata", {}).get("user_id")
    plan_type = session.get("metadata", {}).get("plan_type")

    if not user_id or not plan_type or plan_type not in PLAN_CONFIG:
        return

    # Update order status
    order = (
        db.query(Order)
        .filter(Order.stripe_session_id == session["id"])
        .first()
    )
    if order:
        order.status = "paid"

    # Grant credits
    plan = PLAN_CONFIG[plan_type]
    from datetime import datetime, timedelta, timezone

    expires_at = None
    if plan["expires"]:
        if plan_type == "monthly_10":
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        elif plan_type == "yearly_15":
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    credit = Credit(
        user_id=user_id,
        total=plan["credits"],
        used=0,
        order_id=order.id if order else None,
        expires_at=expires_at,
    )
    db.add(credit)
    db.commit()
