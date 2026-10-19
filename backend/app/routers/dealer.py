from __future__ import annotations
from fastapi import APIRouter, Depends
from app.auth import require_roles
from app.models.auth import User
from pydantic import BaseModel
from app.database import get_db
from app.services.dealer_service import (
    get_dealer_dashboard, get_smart_orders, get_dealer_alerts,
)
from app.models import Dealer, DealerOrder
from app.schemas.orders import CustomerOrderStatusUpdate
from datetime import datetime

router = APIRouter(dependencies=[Depends(require_roles("dealer"))])


class OrderCreate(BaseModel):
    sku_id: int
    quantity: int


@router.get("/{dealer_id}/dashboard")
def dealer_dashboard(dealer_id: int, db=Depends(get_db)):
    return get_dealer_dashboard(db, dealer_id)


@router.get("/{dealer_id}/smart-orders")
def smart_orders(dealer_id: int, db=Depends(get_db)):
    return get_smart_orders(db, dealer_id)


from datetime import datetime, timezone

@router.post("/{dealer_id}/orders")
def place_order(dealer_id: int, order: OrderCreate, db=Depends(get_db)):
    new_order = DealerOrder(
        dealer_id=dealer_id,
        sku_id=order.sku_id,
        quantity=order.quantity,
        order_date=datetime.now(timezone.utc),
        status="placed",
        is_ai_suggested=False,
        order_source="manual",
        savings_amount=0.0,
    )
    db.add(new_order)
    db.commit()
    return {"success": True, "order_id": new_order.id, "status": "placed"}


@router.post("/{dealer_id}/orders/bundle")
def accept_bundle(dealer_id: int, db=Depends(get_db)):
    """Accept all AI-recommended orders at once."""
    recs = get_smart_orders(db, dealer_id)
    total_savings = 0
    orders_placed = 0

    for rec in recs:
        if rec["urgency"] in ("CRITICAL", "RECOMMENDED"):
            order = DealerOrder(
                dealer_id=dealer_id,
                sku_id=rec["sku_id"],
                quantity=rec["recommended_qty"],
                order_date=datetime.now(timezone.utc),
                status="placed",
                is_ai_suggested=True,
                order_source="ai_recommendation",
                savings_amount=rec["savings_amount"],
            )
            db.add(order)
            total_savings += rec["savings_amount"]
            orders_placed += 1

    db.commit()
    return {
        "success": True,
        "orders_placed": orders_placed,
        "total_savings": round(total_savings, 0),
        "message": f"Bundle accepted! {orders_placed} orders placed. You saved ₹{total_savings:,.0f}!",
    }


@router.get("/{dealer_id}/orders")
def order_history(dealer_id: int, db=Depends(get_db)):
    orders = db.query(DealerOrder).filter(
        DealerOrder.dealer_id == dealer_id
    ).order_by(DealerOrder.order_date.desc()).limit(50).all()

    return [
        {
            "id": o.id,
            "sku_id": o.sku_id,
            "quantity": o.quantity,
            "order_date": o.order_date.isoformat() if o.order_date else None,
            "status": o.status,
            "is_ai_suggested": o.is_ai_suggested,
            "savings_amount": o.savings_amount,
        }
        for o in orders
    ]


@router.get("/{dealer_id}/alerts")
def dealer_alerts(dealer_id: int, db=Depends(get_db)):
    return get_dealer_alerts(db, dealer_id)


@router.get("/{dealer_id}/customer-requests")
def dealer_customer_requests(dealer_id: int, db=Depends(get_db)):
    """Fetch customer lead / order requests assigned to this dealership."""
    from app.models import CustomerOrderRequest, Shade, Product
    requests = db.query(CustomerOrderRequest).filter(
        CustomerOrderRequest.dealer_id == dealer_id
    ).all()

    shades_by_id = {s.id: s for s in db.query(Shade).all()}
    prods_by_id = {p.id: p for p in db.query(Product).all()}

    results = []
    for r in requests:
        shade = shades_by_id.get(r.shade_id)
        prod = prods_by_id.get(shade.product_id) if shade else None
        results.append({
            "id": r.id,
            "customer_name": r.customer_name,
            "customer_phone": r.customer_phone,
            "shade_name": shade.shade_name if shade else "",
            "shade_code": shade.shade_code if shade else "",
            "hex_color": shade.hex_color if shade else "#000",
            "product_name": prod.name if prod else "",
            "size_preference": r.size_preference,
            "status": r.status,
            "created_at": r.created_at.isoformat() if getattr(r, "created_at", None) else None,
        })
    return sorted(results, key=lambda x: x["id"], reverse=True)


@router.patch("/{dealer_id}/customer-requests/{request_id}")
def update_customer_request_status(
    dealer_id: int,
    request_id: int,
    body: CustomerOrderStatusUpdate,
    db=Depends(get_db),
):
    """Update status of customer order request (e.g. contacted, fulfilled, cancelled)."""
    from app.models import CustomerOrderRequest
    req = db.query(CustomerOrderRequest).filter(
        CustomerOrderRequest.id == request_id,
        CustomerOrderRequest.dealer_id == dealer_id,
    ).first()
    if not req:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Customer order request not found for this dealer")

    req.status = body.status
    db.commit()
    return {"success": True, "request_id": req.id, "status": req.status}

