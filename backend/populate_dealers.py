from __future__ import annotations
import os
import sys
from pathlib import Path
import random
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal
from app.models import Dealer, Warehouse, Region, Shade, SKU, CustomerOrderRequest, DealerOrder
from app.models.auth import User
from app.auth import hash_password
from seed.geography import DEALER_NAMES, DEALER_LOCATIONS, WAREHOUSES

def populate_dealers():
    db = SessionLocal()
    print("=" * 60)
    print("  Populating 50 Dealers Across India")
    print("=" * 60)

    warehouses = db.query(Warehouse).all()
    if not warehouses:
        print("Error: No warehouses found. Please run populate_shades first.")
        return

    existing_dealers = {d.name: d for d in db.query(Dealer).all()}
    dealers_added = 0

    rng = random.Random(101)
    tiers = ["Platinum"] * 10 + ["Gold"] * 18 + ["Silver"] * 22
    rng.shuffle(tiers)

    new_dealers = []
    for i, (name, loc) in enumerate(zip(DEALER_NAMES, DEALER_LOCATIONS)):
        if name not in existing_dealers:
            wh_idx = min(loc["wh_idx"], len(warehouses) - 1)
            wh = warehouses[wh_idx]

            dealer = Dealer(
                name=name,
                code=f"DLR-{loc['city'][:3].upper()}-{i + 1:03d}",
                region_id=wh.region_id,
                warehouse_id=wh.id,
                city=loc["city"],
                state=loc["state"],
                latitude=loc["lat"],
                longitude=loc["lng"],
                tier=tiers[i],
                credit_limit=float(rng.choice([350000, 500000, 750000, 1000000])),
                performance_score=round(float(rng.uniform(65, 96)), 1),
            )
            db.add(dealer)
            new_dealers.append(dealer)
            dealers_added += 1

    if new_dealers:
        db.flush()
        for d in new_dealers:
            existing_dealers[d.name] = d

    print(f"Dealers added: {dealers_added} (Total now: {len(db.query(Dealer).all())})")

    # Seed sample customer orders and restock orders for dealers
    all_dealers = db.query(Dealer).all()
    all_shades = db.query(Shade).all()
    all_skus = db.query(SKU).all()

    existing_requests = len(db.query(CustomerOrderRequest).all())
    customer_names = [
        "Aarav Patel", "Rohan Verma", "Priya Sharma", "Ananya Iyer",
        "Vikram Malhotra", "Sneha Kulkarni", "Aditya Nair", "Pooja Das",
        "Karan Singhal", "Neha Joshi", "Deepak Rao", "Sunita Sen"
    ]

    requests_added = 0
    if existing_requests < 15 and all_shades and all_dealers:
        sizes = ["1L", "4L", "10L", "20L"]
        statuses = ["requested", "contacted", "fulfilled"]

        for i, cname in enumerate(customer_names):
            shade = all_shades[i % len(all_shades)]
            dealer = all_dealers[i % len(all_dealers)]

            req = CustomerOrderRequest(
                customer_name=cname,
                customer_phone=f"+91 98{rng.randint(10000000, 99999999)}",
                shade_id=shade.id,
                size_preference=rng.choice(sizes),
                dealer_id=dealer.id,
                status=rng.choice(statuses),
                created_at=datetime.now(timezone.utc) - timedelta(days=rng.randint(0, 10)),
            )
            db.add(req)
            requests_added += 1

    # Ensure dealer restock orders exist
    orders_added = 0
    existing_orders = len(db.query(DealerOrder).all())
    if existing_orders < 40 and all_skus and all_dealers:
        for dealer in all_dealers[:20]:
            for _ in range(2):
                sku = rng.choice(all_skus)
                status = rng.choice(["delivered", "dispatched", "confirmed", "recommended"])
                dorder = DealerOrder(
                    dealer_id=dealer.id,
                    sku_id=sku.id,
                    quantity=int(rng.choice([20, 50, 100, 200])),
                    order_date=datetime.now(timezone.utc) - timedelta(days=rng.randint(1, 30)),
                    status=status,
                    is_ai_suggested=rng.choice([True, False]),
                    order_source="ai_recommendation" if rng.choice([True, False]) else "manual",
                    savings_amount=round(float(rng.uniform(500, 4500)), 2),
                )
                db.add(dorder)
                orders_added += 1

    db.commit()
    print(f"Sample Customer Requests added: {requests_added}")
    print(f"Sample Dealer Orders added: {orders_added}")
    print("Dealers population complete!")

if __name__ == "__main__":
    populate_dealers()
