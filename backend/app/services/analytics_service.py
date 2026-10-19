from datetime import date

from app.models import (
    InventoryLevel, InventoryTransfer, Warehouse, SKU, Shade,
    Dealer, DealerOrder, SalesHistory,
)


def get_dashboard_summary(db) -> dict:
    levels = db.query(InventoryLevel).all()
    total_revenue = sum(
        sale.revenue or 0
        for sale in db.query(SalesHistory).filter(SalesHistory.date >= date(2025, 10, 1)).all()
    )
    sku_by_id = {sku.id: sku for sku in db.query(SKU).all()}
    revenue_at_risk = 0
    for level in levels:
        if level.days_of_cover < 7:
            sku = sku_by_id.get(level.sku_id)
            if sku:
                daily_demand = level.current_stock / max(level.days_of_cover, 0.1)
                revenue_at_risk += daily_demand * max(0, 7 - level.days_of_cover) * sku.mrp

    return {
        "total_skus": db.query(SKU).count(),
        "total_warehouses": db.query(Warehouse).count(),
        "total_dealers": db.query(Dealer).count(),
        "total_revenue_mtd": round(total_revenue, 0),
        "stockout_count": sum(1 for level in levels if level.days_of_cover < 3),
        "pending_transfers": db.query(InventoryTransfer).filter(
            InventoryTransfer.status == "PENDING"
        ).count(),
        "revenue_at_risk": round(revenue_at_risk, 0),
        "dead_stock_count": sum(1 for level in levels if level.days_of_cover > 90),
    }


def get_dealer_performance(db, region_id: int | None = None) -> list[dict]:
    dealers = db.query(Dealer)
    if region_id:
        dealers = dealers.filter(Dealer.region_id == region_id)
    dealers = dealers.order_by(Dealer.performance_score.desc()).all()
    orders = db.query(DealerOrder).all()
    sku_by_id = {sku.id: sku for sku in db.query(SKU).all()}

    result = []
    for dealer in dealers:
        dealer_orders = [order for order in orders if order.dealer_id == dealer.id]
        delivered = [order for order in dealer_orders if order.status == "delivered"]
        ai_orders = [order for order in dealer_orders if order.is_ai_suggested]
        total_revenue = sum(
            order.quantity * (
                sku_by_id[order.sku_id].mrp
                if order.sku_id in sku_by_id and sku_by_id[order.sku_id].mrp
                else 500
            )
            for order in delivered
        )
        result.append({
            "id": dealer.id,
            "name": dealer.name,
            "code": dealer.code,
            "city": dealer.city,
            "state": dealer.state,
            "tier": dealer.tier,
            "performance_score": dealer.performance_score,
            "total_orders": len(dealer_orders),
            "total_revenue": round(total_revenue, 0),
            "ai_adoption_rate": round(len(ai_orders) / max(len(dealer_orders), 1) * 100, 1),
            "trend": "up" if dealer.performance_score > 60 else "down",
        })
    return result


def get_top_skus(db, limit: int = 10) -> list[dict]:
    sales = [
        sale for sale in db.query(SalesHistory).all()
        if sale.date >= date(2025, 9, 1)
    ]
    totals: dict[int, dict[str, float]] = {}
    for sale in sales:
        values = totals.setdefault(sale.sku_id, {"revenue": 0, "quantity": 0})
        values["revenue"] += sale.revenue or 0
        values["quantity"] += sale.quantity_sold or 0

    sku_by_id = {sku.id: sku for sku in db.query(SKU).all()}
    shade_by_id = {shade.id: shade for shade in db.query(Shade).all()}
    top = sorted(totals.items(), key=lambda item: item[1]["revenue"], reverse=True)[:limit]
    result = []
    for sku_id, values in top:
        sku = sku_by_id.get(sku_id)
        shade = shade_by_id.get(sku.shade_id) if sku else None
        result.append({
            "sku_id": sku_id,
            "sku_code": sku.sku_code if sku else "",
            "shade_name": shade.shade_name if shade else "",
            "shade_hex": shade.hex_color if shade else "#000",
            "size": sku.size if sku else "",
            "total_revenue": round(values["revenue"], 0),
            "total_quantity": values["quantity"],
        })
    return result
