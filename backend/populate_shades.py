from __future__ import annotations
import os
import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal
from app.models import Product, Shade, SKU, Warehouse, InventoryLevel, Region
from app.models.auth import User
from app.auth import hash_password
from seed.paint_catalog import SHADES, PRODUCTS, SIZE_MULTIPLIERS, hex_to_rgb, get_shade_code, get_sku_code
from seed.geography import REGIONS, WAREHOUSES

def populate():
    db = SessionLocal()
    print("=" * 60)
    print("  Fast Populating 100+ Shades and Inventory Levels")
    print("=" * 60)

    # 1. Ensure Products
    existing_products = {p.name: p for p in db.query(Product).all()}
    products_list = []
    for p_data in PRODUCTS:
        if p_data["name"] not in existing_products:
            p = Product(**p_data)
            db.add(p)
            db.flush()
            existing_products[p.name] = p
        products_list.append(existing_products[p_data["name"]])
    print(f"Products available: {len(products_list)}")

    # 2. Ensure Regions and Warehouses
    existing_regions = {r.name: r for r in db.query(Region).all()}
    regions_list = []
    for r_data in REGIONS:
        if r_data["name"] not in existing_regions:
            r = Region(**r_data)
            db.add(r)
            db.flush()
            existing_regions[r.name] = r
        regions_list.append(existing_regions[r_data["name"]])

    existing_wh = {w.code: w for w in db.query(Warehouse).all()}
    warehouses_list = []
    for wh_data in WAREHOUSES:
        if wh_data["code"] not in existing_wh:
            reg = regions_list[wh_data["region_idx"]]
            wh = Warehouse(
                name=wh_data["name"],
                code=wh_data["code"],
                region_id=reg.id,
                city=wh_data["city"],
                state=wh_data["state"],
                latitude=wh_data["lat"],
                longitude=wh_data["lng"],
                capacity_litres=wh_data["capacity"],
            )
            db.add(wh)
            db.flush()
            existing_wh[wh.code] = wh
        warehouses_list.append(existing_wh[wh_data["code"]])
    print(f"Warehouses available: {len(warehouses_list)}")

    # 3. Add Shades and SKUs
    existing_shades = {s.shade_name: s for s in db.query(Shade).all()}
    existing_skus = {sku.sku_code: sku for sku in db.query(SKU).all()}
    existing_levels = {(l.warehouse_id, l.sku_id) for l in db.query(InventoryLevel).all()}

    shades_added = 0
    skus_added = 0
    inv_levels_added = 0
    rng = random.Random(42)

    new_shades = []
    for family, shade_tuples in SHADES.items():
        for idx, (name, hex_color, prod_idx, is_trending) in enumerate(shade_tuples):
            if name not in existing_shades:
                r, g, b = hex_to_rgb(hex_color)
                prod = products_list[prod_idx]
                shade = Shade(
                    product_id=prod.id,
                    shade_code=get_shade_code(family, idx),
                    shade_name=name,
                    hex_color=hex_color,
                    rgb_r=r,
                    rgb_g=g,
                    rgb_b=b,
                    shade_family=family,
                    is_trending=is_trending,
                )
                db.add(shade)
                new_shades.append((shade, name, prod))
                shades_added += 1

    if new_shades:
        db.flush()
        for shade, name, _ in new_shades:
            existing_shades[name] = shade

    print(f"Shades added: {shades_added}")

    # Now create SKUs
    new_skus = []
    for family, shade_tuples in SHADES.items():
        for idx, (name, hex_color, prod_idx, is_trending) in enumerate(shade_tuples):
            shade = existing_shades[name]
            prod = next((p for p in products_list if p.id == shade.product_id), products_list[0])
            for size, mults in SIZE_MULTIPLIERS.items():
                sku_code = get_sku_code(prod.name, shade.shade_code, size)
                if sku_code not in existing_skus:
                    sku = SKU(
                        shade_id=shade.id,
                        size=size,
                        sku_code=sku_code,
                        unit_cost=round(prod.price_per_litre * mults["cost_mult"] * 0.65, 2),
                        mrp=round(prod.price_per_litre * mults["mrp_mult"], 2),
                    )
                    db.add(sku)
                    new_skus.append((sku, sku_code))
                    skus_added += 1

    if new_skus:
        db.flush()
        for sku, sku_code in new_skus:
            existing_skus[sku_code] = sku

    print(f"SKUs added: {skus_added}")

    # Now create inventory levels
    for sku_code, sku in existing_skus.items():
        for wh in warehouses_list:
            if (wh.id, sku.id) not in existing_levels:
                stock = int(rng.uniform(80, 1500))
                daily = rng.uniform(5, 25)
                doc = round(stock / max(daily, 0.1), 1)

                inv = InventoryLevel(
                    warehouse_id=wh.id,
                    sku_id=sku.id,
                    current_stock=stock,
                    reorder_point=int(daily * 7),
                    max_capacity=int(stock * 2.5),
                    days_of_cover=doc,
                    last_updated=None,
                )
                db.add(inv)
                existing_levels.add((wh.id, sku.id))
                inv_levels_added += 1

    print(f"Inventory levels added: {inv_levels_added}")

    # Ensure demo users exist
    demo_users = [
        ("admin@moderncolours.local", "AdminPass123!", "admin", None),
        ("dealer@moderncolours.local", "DealerPass123!", "dealer", 1),
        ("customer@moderncolours.local", "CustomerPass123!", "customer", None),
    ]
    for email, pw, role, dealer_id in demo_users:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            u = User(
                email=email,
                password_hash=hash_password(pw),
                role=role,
                status="active",
                dealer_id=dealer_id,
            )
            db.add(u)

    db.commit()
    print("Commit complete!")
    print(f"Total in Database:")
    print(f"  Shades: {len(db.query(Shade).all())}")
    print(f"  SKUs: {len(db.query(SKU).all())}")
    print(f"  Inventory Levels: {len(db.query(InventoryLevel).all())}")

if __name__ == "__main__":
    populate()
