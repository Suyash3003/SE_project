from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from app.auth import require_roles, get_current_user
from app.models.auth import User
from app.database import get_db
from app.models import Shade, SKU, Product, Dealer, InventoryLevel, CustomerOrderRequest
from app.schemas.orders import OrderRequestCreate
from app.schemas.snap_find import SnapFindRequest
from datetime import datetime, timezone
import math

router = APIRouter(dependencies=[Depends(require_roles("customer"))])

def get_shades(
    family: str = None, category: str = None, trending: bool = None,
    db=Depends(get_db),
):
    query = db.query(Shade)
    if family:
        query = query.filter(Shade.shade_family == family)
    if trending is not None:
        query = query.filter(Shade.is_trending == trending)

    shades = query.all()
    result = []
    for s in shades:
        product = db.query(Product).filter(Product.id == s.product_id).first()
        if category and product and product.category != category:
            continue
        result.append({
            "id": s.id,
            "shade_code": s.shade_code,
            "shade_name": s.shade_name,
            "hex_color": s.hex_color,
            "shade_family": s.shade_family,
            "is_trending": s.is_trending,
            "product_name": product.name if product else "",
            "product_category": product.category if product else "",
            "finish": product.finish if product else "",
        })
    return result


@router.get("/shades/{shade_id}")
def get_shade_detail(shade_id: int, db=Depends(get_db)):
    shade = db.query(Shade).filter(Shade.id == shade_id).first()
    if not shade:
        return {"error": "Shade not found"}

    product = db.query(Product).filter(Product.id == shade.product_id).first()
    skus = db.query(SKU).filter(SKU.shade_id == shade.id).all()

    return {
        "id": shade.id,
        "shade_code": shade.shade_code,
        "shade_name": shade.shade_name,
        "hex_color": shade.hex_color,
        "rgb": {"r": shade.rgb_r, "g": shade.rgb_g, "b": shade.rgb_b},
        "shade_family": shade.shade_family,
        "is_trending": shade.is_trending,
        "product": {
            "name": product.name if product else "",
            "category": product.category if product else "",
            "finish": product.finish if product else "",
            "base_type": product.base_type if product else "",
        },
        "sizes": [
            {"size": sku.size, "sku_code": sku.sku_code, "mrp": sku.mrp, "sku_id": sku.id}
            for sku in sorted(skus, key=lambda x: float(x.size.replace("L", "")))
        ],
    }


@router.get("/shades/{shade_id}/availability")
def shade_availability(shade_id: int, lat: float = 19.07, lng: float = 72.87, db=Depends(get_db)):
    """Find nearby dealers with stock for this shade."""
    shade = db.query(Shade).filter(Shade.id == shade_id).first()
    if not shade:
        return []

    # Get 4L SKU for this shade
    sku = db.query(SKU).filter(SKU.shade_id == shade_id, SKU.size == "4L").first()
    if not sku:
        return []

    dealers = db.query(Dealer).all()
    results = []

    for dealer in dealers:
        # Calculate distance
        dist = _haversine(lat, lng, dealer.latitude, dealer.longitude)
        if dist > 50:  # 50km radius
            continue

        # Check stock at dealer's warehouse
        level = db.query(InventoryLevel).filter(
            InventoryLevel.warehouse_id == dealer.warehouse_id,
            InventoryLevel.sku_id == sku.id,
        ).first()

        stock = level.current_stock if level else 0
        if stock > 50:
            stock_status = "In Stock"
        elif stock > 0:
            stock_status = "Low Stock"
        else:
            stock_status = "Out of Stock"

        results.append({
            "dealer_id": dealer.id,
            "dealer_name": dealer.name,
            "city": dealer.city,
            "distance_km": round(dist, 1),
            "stock_status": stock_status,
            "stock_qty": stock,
            "latitude": dealer.latitude,
            "longitude": dealer.longitude,
        })

    return sorted(results, key=lambda x: x["distance_km"])[:10]


@router.get("/dealers/nearby")
def nearby_dealers(lat: float = 19.07, lng: float = 72.87, db=Depends(get_db)):
    dealers = db.query(Dealer).all()
    results = []
    for d in dealers:
        dist = _haversine(lat, lng, d.latitude, d.longitude)
        if dist < 50:
            results.append({
                "id": d.id,
                "name": d.name,
                "city": d.city,
                "distance_km": round(dist, 1),
                "tier": d.tier,
                "latitude": d.latitude,
                "longitude": d.longitude,
            })
    return sorted(results, key=lambda x: x["distance_km"])[:10]


@router.post("/order-request")
def create_order_request(
    req: OrderRequestCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    from fastapi import HTTPException
    dealer = db.query(Dealer).filter(Dealer.id == req.dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Selected dealer not found")

    shade = db.query(Shade).filter(Shade.id == req.shade_id).first()
    if not shade:
        raise HTTPException(status_code=404, detail="Selected color shade not found")

    order_req = CustomerOrderRequest(
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        shade_id=req.shade_id,
        size_preference=req.size_preference,
        dealer_id=req.dealer_id,
        quantity=getattr(req, "quantity", 1),
        delivery_address=getattr(req, "delivery_address", ""),
        notes=getattr(req, "notes", ""),
        user_id=current_user.id if current_user else None,
        status="requested",
        created_at=datetime.now(timezone.utc),
    )
    db.add(order_req)
    db.commit()

    return {
        "success": True,
        "request_id": order_req.id,
        "message": f"Order for {req.size_preference} of {shade.shade_name} placed with {dealer.name}!",
        "order": {
            "id": order_req.id,
            "dealer_name": dealer.name,
            "dealer_city": dealer.city,
            "shade_name": shade.shade_name,
            "shade_code": shade.shade_code,
            "hex_color": shade.hex_color,
            "size": req.size_preference,
            "quantity": getattr(req, "quantity", 1),
            "status": "requested",
            "created_at": order_req.created_at.isoformat() if order_req.created_at else None,
        }
    }


@router.get("/orders")
def get_customer_orders(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Retrieve paint order history for the logged-in customer."""
    all_requests = db.query(CustomerOrderRequest).all()

    if current_user:
        user_requests = [
            r for r in all_requests
            if getattr(r, "user_id", None) == current_user.id
            or (current_user.phone and getattr(r, "customer_phone", None) == current_user.phone)
        ]
    else:
        user_requests = []

    shades_by_id = {s.id: s for s in db.query(Shade).all()}
    prods_by_id = {p.id: p for p in db.query(Product).all()}
    dealers_by_id = {d.id: d for d in db.query(Dealer).all()}
    skus = db.query(SKU).all()

    results = []
    for r in user_requests:
        shade = shades_by_id.get(r.shade_id)
        prod = prods_by_id.get(shade.product_id) if shade else None
        dealer = dealers_by_id.get(r.dealer_id)
        
        sku = next((s for s in skus if s.shade_id == r.shade_id and s.size == r.size_preference), None)
        est_price = sku.mrp if sku else (prod.price_per_litre * 3.6 if prod else 1500)
        qty = getattr(r, "quantity", 1) or 1

        results.append({
            "id": r.id,
            "customer_name": r.customer_name,
            "customer_phone": r.customer_phone,
            "dealer_id": r.dealer_id,
            "dealer_name": dealer.name if dealer else f"Dealer #{r.dealer_id}",
            "dealer_city": dealer.city if dealer else "",
            "dealer_state": dealer.state if dealer else "",
            "shade_id": r.shade_id,
            "shade_name": shade.shade_name if shade else "",
            "shade_code": shade.shade_code if shade else "",
            "hex_color": shade.hex_color if shade else "#CCC",
            "product_name": prod.name if prod else "",
            "size": r.size_preference,
            "quantity": qty,
            "estimated_amount": round(est_price * qty, 0),
            "delivery_address": getattr(r, "delivery_address", "") or "",
            "status": r.status,
            "created_at": r.created_at.isoformat() if getattr(r, "created_at", None) else None,
        })

    return sorted(results, key=lambda x: x["id"], reverse=True)


@router.get("/dealers")
def get_all_dealers(
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    db=Depends(get_db),
):
    """List all 50+ authorized dealers across India with distance calculation."""
    dealers = db.query(Dealer).all()
    if city and city.lower() != "all":
        dealers = [d for d in dealers if d.city.lower() == city.lower()]

    results = []
    for d in dealers:
        distance = None
        if lat is not None and lng is not None and d.latitude and d.longitude:
            distance = round(_haversine(lat, lng, d.latitude, d.longitude), 1)

        results.append({
            "id": d.id,
            "name": d.name,
            "code": d.code,
            "city": d.city,
            "state": d.state,
            "tier": d.tier,
            "performance_score": d.performance_score,
            "distance_km": distance,
            "latitude": d.latitude,
            "longitude": d.longitude,
        })

    if lat is not None and lng is not None:
        return sorted(results, key=lambda x: (x["distance_km"] is None, x["distance_km"]))
    return sorted(results, key=lambda x: x["name"])



@router.post("/snap-find")
async def snap_and_find(
    hex_color: str = "#FFD700",
    req: Optional[SnapFindRequest] = None,
    db=Depends(get_db),
):
    """
    Find closest shade match for a given hex color.
    Accepts hex_color via request body or query parameter with robust validation.
    """
    raw_hex = req.hex_color if req else hex_color
    clean_hex = raw_hex.strip()
    if not clean_hex.startswith("#"):
        clean_hex = f"#{clean_hex}"

    import re
    if not re.match(r"^#[0-9a-fA-F]{6}$", clean_hex):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid hex color '{raw_hex}'. Please provide a valid 6-character hex code, e.g. #FFD700",
        )

    target_r, target_g, target_b = _hex_to_rgb(clean_hex)

    # Rank all catalog shades by Euclidean RGB distance
    shades = db.query(Shade).all()
    if not shades:
        raise HTTPException(status_code=404, detail="No catalog shades available")

    ranked = []
    for shade in shades:
        dist = math.sqrt(
            (shade.rgb_r - target_r) ** 2 +
            (shade.rgb_g - target_g) ** 2 +
            (shade.rgb_b - target_b) ** 2
        )
        ranked.append((dist, shade))

    ranked.sort(key=lambda x: x[0])
    best_dist, best_match = ranked[0]
    product = db.query(Product).filter(Product.id == best_match.product_id).first()

    alternatives = []
    for dist, alt_shade in ranked[1:4]:
        alt_prod = db.query(Product).filter(Product.id == alt_shade.product_id).first()
        alternatives.append({
            "shade_id": alt_shade.id,
            "shade_name": alt_shade.shade_name,
            "shade_code": alt_shade.shade_code,
            "hex_color": alt_shade.hex_color,
            "shade_family": alt_shade.shade_family,
            "product_name": alt_prod.name if alt_prod else "",
            "confidence": round(max(0, 100 - dist / 4.41), 1),
        })

    return {
        "detected_color": {"hex": clean_hex.upper(), "rgb": {"r": target_r, "g": target_g, "b": target_b}},
        "match": {
            "shade_name": best_match.shade_name,
            "shade_code": best_match.shade_code,
            "hex_color": best_match.hex_color,
            "shade_family": best_match.shade_family,
            "product_name": product.name if product else "",
            "confidence": round(max(0, 100 - best_dist / 4.41), 1),
        },
        "shade_id": best_match.id,
        "alternatives": alternatives,
        "sampling_method": "multi_pixel_euclidean_ranking",
    }


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

