import pytest
from app.services.inventory_service import approve_transfer
from app.models import InventoryLevel, InventoryTransfer, DealerOrder
from app.services.analytics_service import get_dealer_performance


def test_approve_transfer_and_days_of_cover(db):
    # Initial state: Mumbai has 100 units, 20 days cover (5 units/day)
    # Pune has 20 units, 4 days cover (5 units/day)
    res = approve_transfer(db, 1)
    assert res["success"] is True

    # Check updated levels
    from_level = db.query(InventoryLevel).filter(
        InventoryLevel.warehouse_id == 1,
        InventoryLevel.sku_id == 10,
    ).first()
    to_level = db.query(InventoryLevel).filter(
        InventoryLevel.warehouse_id == 2,
        InventoryLevel.sku_id == 10,
    ).first()

    assert from_level.current_stock == 50
    # 50 units / (5 units/day) = 10 days of cover
    assert from_level.days_of_cover == 10.0

    assert to_level.current_stock == 70
    # 70 units / (5 units/day) = 14 days of cover
    assert to_level.days_of_cover == 14.0


def test_approve_transfer_idempotency(db):
    res_first = approve_transfer(db, 1)
    assert res_first["success"] is True

    # Attempt repeat approval
    res_repeat = approve_transfer(db, 1)
    assert res_repeat["success"] is False
    assert "already" in res_repeat["message"].lower()

    # Verify inventory was NOT deducted again
    from_level = db.query(InventoryLevel).filter(
        InventoryLevel.warehouse_id == 1,
        InventoryLevel.sku_id == 10,
    ).first()
    assert from_level.current_stock == 50


def test_dealer_revenue_uses_real_sku_mrp(db):
    # Place a delivered order for 10 units of SKU 10 (MRP = 1520.0)
    order = DealerOrder(
        dealer_id=1,
        sku_id=10,
        quantity=10,
        status="delivered",
        is_ai_suggested=False,
    )
    db.add(order)
    db.commit()

    perf = get_dealer_performance(db)
    assert len(perf) > 0
    dealer_perf = next(p for p in perf if p["id"] == 1)
    # 10 * 1520.0 = 15,200 (NOT 10 * 500 = 5000)
    assert dealer_perf["total_revenue"] == 15200
