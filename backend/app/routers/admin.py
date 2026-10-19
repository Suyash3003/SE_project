from __future__ import annotations
from fastapi import APIRouter, Depends
from app.auth import require_roles
from app.models.auth import User
from app.database import get_db
from app.services.analytics_service import get_dashboard_summary, get_dealer_performance, get_top_skus
from app.services.inventory_service import (
    get_warehouse_map_data, get_warehouse_inventory,
    get_recommended_transfers, approve_transfer, get_dead_stock,
)
from app.schemas import CreateShadeSchema, AddStockSchema

router = APIRouter(dependencies=[Depends(require_roles("admin"))])


@router.get("/dashboard/summary")
def dashboard_summary(db=Depends(get_db)):
    return get_dashboard_summary(db)


@router.get("/inventory/map")
def inventory_map(db=Depends(get_db)):
    return get_warehouse_map_data(db)


@router.get("/inventory/warehouse/{warehouse_id}")
def warehouse_inventory(warehouse_id: int, db=Depends(get_db)):
    return get_warehouse_inventory(db, warehouse_id)


@router.get("/dead-stock")
def dead_stock(db=Depends(get_db)):
    return get_dead_stock(db)


@router.get("/transfers/recommended")
def recommended_transfers(db=Depends(get_db)):
    return get_recommended_transfers(db)


@router.post("/transfers/{transfer_id}/approve")
def approve_transfer_endpoint(transfer_id: int, db=Depends(get_db)):
    return approve_transfer(db, transfer_id)


@router.post("/transfers/{transfer_id}/auto-balance")
def auto_balance(transfer_id: int, db=Depends(get_db)):
    return approve_transfer(db, transfer_id)


@router.get("/dealers/performance")
def dealer_performance(region_id: int = None, db=Depends(get_db)):
    return get_dealer_performance(db, region_id)


@router.get("/top-skus")
def top_skus(limit: int = 10, db=Depends(get_db)):
    return get_top_skus(db, limit)


@router.get("/customer-requests")
def all_customer_requests(db=Depends(get_db)):
    """Supply chain overview of all customer order leads and fulfillment statuses."""
    from app.models import CustomerOrderRequest, Shade, Product, Dealer
    requests = db.query(CustomerOrderRequest).all()
    shades_by_id = {s.id: s for s in db.query(Shade).all()}
    prods_by_id = {p.id: p for p in db.query(Product).all()}
    dealers_by_id = {d.id: d for d in db.query(Dealer).all()}

    results = []
    for r in requests:
        shade = shades_by_id.get(r.shade_id)
        prod = prods_by_id.get(shade.product_id) if shade else None
        dealer = dealers_by_id.get(r.dealer_id)
        results.append({
            "id": r.id,
            "customer_name": r.customer_name,
            "customer_phone": r.customer_phone,
            "dealer_name": dealer.name if dealer else f"Dealer #{r.dealer_id}",
            "dealer_city": dealer.city if dealer else "",
            "shade_name": shade.shade_name if shade else "",
            "shade_code": shade.shade_code if shade else "",
            "hex_color": shade.hex_color if shade else "#000",
            "product_name": prod.name if prod else "",
            "size_preference": r.size_preference,
            "status": r.status,
            "created_at": r.created_at.isoformat() if getattr(r, "created_at", None) else None,
        })
    return sorted(results, key=lambda x: x["id"], reverse=True)


@router.get("/products")
def list_products(db=Depends(get_db)):
    from app.models import Product
    products = db.query(Product).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "sub_category": p.sub_category,
            "base_type": p.base_type,
            "finish": p.finish,
            "price_per_litre": p.price_per_litre,
        }
        for p in products
    ]


@router.get("/warehouses")
def list_warehouses(db=Depends(get_db)):
    from app.models import Warehouse
    warehouses = db.query(Warehouse).all()
    return [
        {
            "id": w.id,
            "name": w.name,
            "code": w.code,
            "city": w.city,
            "state": w.state,
            "capacity": w.capacity_litres or 100000,
        }
        for w in warehouses
    ]


@router.get("/catalog/shades")
def list_catalog_shades(family: str = None, search: str = None, db=Depends(get_db)):
    from app.models import Shade, SKU, Product, InventoryLevel
    shades = db.query(Shade).all()
    if family:
        shades = [s for s in shades if s.shade_family.lower() == family.lower()]
    if search:
        s_lower = search.lower()
        shades = [s for s in shades if s_lower in s.shade_name.lower() or s_lower in s.shade_code.lower()]

    products_by_id = {p.id: p for p in db.query(Product).all()}
    skus_by_shade = {}
    for sku in db.query(SKU).all():
        skus_by_shade.setdefault(sku.shade_id, []).append(sku)

    levels_by_sku = {}
    for level in db.query(InventoryLevel).all():
        levels_by_sku.setdefault(level.sku_id, []).append(level)

    results = []
    for s in shades:
        prod = products_by_id.get(s.product_id)
        shade_skus = skus_by_shade.get(s.id, [])
        total_stock = 0
        for sku in shade_skus:
            total_stock += sum(l.current_stock for l in levels_by_sku.get(sku.id, []))

        results.append({
            "id": s.id,
            "shade_code": s.shade_code,
            "shade_name": s.shade_name,
            "hex_color": s.hex_color,
            "shade_family": s.shade_family,
            "is_trending": bool(s.is_trending),
            "product_id": s.product_id,
            "product_name": prod.name if prod else "",
            "product_category": prod.category if prod else "",
            "finish": prod.finish if prod else "",
            "total_stock": total_stock,
            "sku_count": len(shade_skus),
            "skus": [
                {
                    "id": sku.id,
                    "size": sku.size,
                    "sku_code": sku.sku_code,
                    "unit_cost": sku.unit_cost,
                    "mrp": sku.mrp,
                }
                for sku in shade_skus
            ],
        })

    return sorted(results, key=lambda x: x["id"], reverse=True)


@router.post("/catalog/shades")
def create_catalog_shade(payload: CreateShadeSchema, db=Depends(get_db)):
    from app.models import Product, Shade, SKU, Warehouse, InventoryLevel
    from seed.paint_catalog import SIZE_MULTIPLIERS, hex_to_rgb, get_shade_code, get_sku_code
    from fastapi import HTTPException

    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(Shade).filter(Shade.shade_name == payload.shade_name.strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Shade '{payload.shade_name}' already exists")

    family_shades = [s for s in db.query(Shade).all() if s.shade_family == payload.shade_family]
    next_idx = len(family_shades)
    shade_code = get_shade_code(payload.shade_family, next_idx)

    code_exists = db.query(Shade).filter(Shade.shade_code == shade_code).first()
    if code_exists:
        shade_code = f"{shade_code}-{next_idx + 1}"

    r, g, b = hex_to_rgb(payload.hex_color)

    new_shade = Shade(
        product_id=product.id,
        shade_code=shade_code,
        shade_name=payload.shade_name.strip(),
        hex_color=payload.hex_color,
        rgb_r=r,
        rgb_g=g,
        rgb_b=b,
        shade_family=payload.shade_family,
        is_trending=payload.is_trending,
    )
    db.add(new_shade)
    db.flush()

    created_skus = []
    warehouses = db.query(Warehouse).all()
    initial_stock = payload.initial_stock_per_warehouse or 0

    for size, mults in SIZE_MULTIPLIERS.items():
        sku_code = get_sku_code(product.name, new_shade.shade_code, size)
        sku = SKU(
            shade_id=new_shade.id,
            size=size,
            sku_code=sku_code,
            unit_cost=round(product.price_per_litre * mults["cost_mult"] * 0.65, 2),
            mrp=round(product.price_per_litre * mults["mrp_mult"], 2),
        )
        db.add(sku)
        db.flush()
        created_skus.append(sku)

        for wh in warehouses:
            stock = initial_stock
            doc = round(stock / 15.0, 1) if stock > 0 else 0.0
            inv = InventoryLevel(
                warehouse_id=wh.id,
                sku_id=sku.id,
                current_stock=stock,
                reorder_point=max(50, int(stock * 0.2)),
                max_capacity=max(200, int(stock * 2.5)),
                days_of_cover=doc,
                last_updated=None,
            )
            db.add(inv)

    db.commit()

    return {
        "message": f"Color shade '{new_shade.shade_name}' created successfully with {len(created_skus)} SKUs and inventory allocated.",
        "shade": {
            "id": new_shade.id,
            "shade_code": new_shade.shade_code,
            "shade_name": new_shade.shade_name,
            "hex_color": new_shade.hex_color,
            "shade_family": new_shade.shade_family,
            "product_name": product.name,
            "skus_created": len(created_skus),
            "initial_stock_per_warehouse": initial_stock,
        }
    }


@router.post("/inventory/add-stock")
def add_inventory_stock(payload: AddStockSchema, db=Depends(get_db)):
    from app.models import Warehouse, SKU, InventoryLevel
    from fastapi import HTTPException

    wh = db.query(Warehouse).filter(Warehouse.id == payload.warehouse_id).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    sku = db.query(SKU).filter(SKU.id == payload.sku_id).first()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    level = db.query(InventoryLevel).filter(
        InventoryLevel.warehouse_id == payload.warehouse_id,
        InventoryLevel.sku_id == payload.sku_id,
    ).first()

    if not level:
        level = InventoryLevel(
            warehouse_id=payload.warehouse_id,
            sku_id=payload.sku_id,
            current_stock=payload.quantity,
            reorder_point=50,
            max_capacity=payload.quantity * 2,
            days_of_cover=round(payload.quantity / 15.0, 1),
            last_updated=None,
        )
        db.add(level)
    else:
        level.current_stock += payload.quantity
        level.days_of_cover = round(level.current_stock / 15.0, 1)

    db.commit()
    return {
        "message": f"Successfully added {payload.quantity} units to {wh.name}.",
        "warehouse_id": wh.id,
        "warehouse_name": wh.name,
        "sku_code": sku.sku_code,
        "new_stock": level.current_stock,
        "days_of_cover": level.days_of_cover,
    }


