from __future__ import annotations
import pytest
from starlette.testclient import TestClient

def test_catalog_endpoints(client: TestClient, db, admin_headers: dict):
    headers = admin_headers

    # 1. List products
    res = client.get("/api/admin/products", headers=headers)
    assert res.status_code == 200
    products = res.json()
    assert len(products) > 0

    # 2. List warehouses
    res = client.get("/api/admin/warehouses", headers=headers)
    assert res.status_code == 200
    warehouses = res.json()
    assert len(warehouses) > 0

    # 3. Create a new custom color
    payload = {
        "shade_name": "Test Cobalt Spark",
        "hex_color": "#0047AB",
        "shade_family": "Blues",
        "product_id": products[0]["id"],
        "is_trending": True,
        "initial_stock_per_warehouse": 250,
    }
    res = client.post("/api/admin/catalog/shades", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "created successfully" in data["message"]
    shade = data["shade"]
    assert shade["shade_name"] == "Test Cobalt Spark"
    assert shade["skus_created"] == 4

    # 4. Duplicate name should be rejected
    res_dup = client.post("/api/admin/catalog/shades", json=payload, headers=headers)
    assert res_dup.status_code == 400

    # 5. List catalog shades
    res_list = client.get("/api/admin/catalog/shades", headers=headers)
    assert res_list.status_code == 200
    shades = res_list.json()
    created_item = next((s for s in shades if s["shade_name"] == "Test Cobalt Spark"), None)
    assert created_item is not None
    assert len(created_item["skus"]) == 4
    assert created_item["total_stock"] > 0

    # 6. Add stock
    target_sku = created_item["skus"][0]["id"]
    res_stock = client.post(
        "/api/admin/inventory/add-stock",
        json={
            "warehouse_id": warehouses[0]["id"],
            "sku_id": target_sku,
            "quantity": 100,
        },
        headers=headers,
    )
    assert res_stock.status_code == 200
    assert "Successfully added 100 units" in res_stock.json()["message"]
