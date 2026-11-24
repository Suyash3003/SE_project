import os
import tempfile
from pathlib import Path
import pytest
from starlette.testclient import TestClient

# Ensure test configuration
os.environ["ENVIRONMENT"] = "development"
os.environ["JWT_SECRET"] = "modern-colours-test-secret-key-at-least-32-chars-long-secure-2025"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"

import app.config as config
from app.database import SQLiteSession, get_db
from app.models.auth import User
from app.models import (
    Warehouse, Region, Product, Shade, SKU,
    InventoryLevel, InventoryTransfer, Dealer, DealerOrder
)
from app.auth import create_access_token, hash_password
from app.main import app


@pytest.fixture(scope="session")
def test_db_path():
    temp_dir = tempfile.TemporaryDirectory()
    db_file = Path(temp_dir.name) / "test_paintflow.db"
    yield db_file
    temp_dir.cleanup()


@pytest.fixture
def db(test_db_path, monkeypatch):
    monkeypatch.setattr(config, "DATABASE_PATH", test_db_path)
    session = SQLiteSession()
    # Clean previous tables if any
    session.connection.execute("DELETE FROM documents")
    session.connection.commit()

    # Seed core fixtures
    admin = User(
        email="admin@moderncolours.local",
        password_hash=hash_password("AdminPass123!"),
        role="admin",
        status="active",
    )
    dealer_user = User(
        email="dealer@moderncolours.local",
        password_hash=hash_password("DealerPass123!"),
        role="dealer",
        dealer_id=1,
        status="active",
    )
    customer_user = User(
        email="customer@moderncolours.local",
        password_hash=hash_password("CustomerPass123!"),
        role="customer",
        status="active",
    )
    session.add(admin)
    session.add(dealer_user)
    session.add(customer_user)

    reg_west = Region(name="West", states='["Maharashtra"]', id=4)
    reg_north = Region(name="North", states='["Delhi"]', id=1)
    session.add(reg_west)
    session.add(reg_north)

    wh_mumbai = Warehouse(name="Mumbai Central WH", city="Mumbai", region_id=4, latitude=19.07, longitude=72.87, capacity=50000, current_utilization=0.6, id=1)
    wh_pune = Warehouse(name="Pune Depot", city="Pune", region_id=4, latitude=18.52, longitude=73.85, capacity=20000, current_utilization=0.8, id=2)
    session.add(wh_mumbai)
    session.add(wh_pune)

    dealer = Dealer(
        name="Apex Paints Pune",
        code="DLR-PUN-001",
        region_id=4,
        warehouse_id=2,
        city="Pune",
        state="Maharashtra",
        latitude=18.52,
        longitude=73.85,
        tier="Gold",
        credit_limit=500000,
        performance_score=75.0,
        id=1,
    )
    session.add(dealer)

    prod_ext = Product(name="Apex Weathercoat", category="Exterior Wall", sub_category="Premium", base_type="Water-based", finish="Matt", sizes_available='["4L"]', price_per_litre=380.0, id=3)
    session.add(prod_ext)

    shade_red = Shade(product_id=3, shade_code="SH-001", shade_name="Bridal Red", hex_color="#C41E3A", rgb_r=196, rgb_g=30, rgb_b=58, shade_family="Red", is_trending=True, id=1)
    session.add(shade_red)

    sku_red_4l = SKU(shade_id=1, size="4L", sku_code="SKU-RED-4L", unit_cost=1000.0, mrp=1520.0, id=10)
    session.add(sku_red_4l)

    # 100 units at Mumbai with 20 days cover (daily demand = 5 units/day)
    inv_mumbai = InventoryLevel(warehouse_id=1, sku_id=10, current_stock=100, days_of_cover=20.0, min_threshold=10, max_capacity=500)
    # 20 units at Pune with 4 days cover (daily demand = 5 units/day)
    inv_pune = InventoryLevel(warehouse_id=2, sku_id=10, current_stock=20, days_of_cover=4.0, min_threshold=15, max_capacity=200)
    session.add(inv_mumbai)
    session.add(inv_pune)

    transfer = InventoryTransfer(
        from_warehouse_id=1,
        to_warehouse_id=2,
        sku_id=10,
        quantity=50,
        status="PENDING",
        reason="Stockout prevention",
        id=1,
    )
    session.add(transfer)

    session.commit()
    yield session
    session.close()


@pytest.fixture
def client(db, test_db_path, monkeypatch):
    monkeypatch.setattr(config, "DATABASE_PATH", test_db_path)

    def override_get_db():
        session = SQLiteSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()



@pytest.fixture
def admin_headers(db):
    user = db.query(User).filter(User.role == "admin").first()
    token = create_access_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def dealer_headers(db):
    user = db.query(User).filter(User.role == "dealer").first()
    token = create_access_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def customer_headers(db):
    user = db.query(User).filter(User.role == "customer").first()
    token = create_access_token(user)
    return {"Authorization": f"Bearer {token}"}
