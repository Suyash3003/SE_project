import pytest


def test_snap_and_find_valid_color(client, customer_headers):
    res = client.post("/api/customer/snap-find", params={"hex_color": "#C41E3A"}, headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert "match" in data
    assert data["match"]["shade_name"] == "Bridal Red"
    assert "alternatives" in data
    assert data["match"]["confidence"] > 90


def test_snap_and_find_invalid_hex(client, customer_headers):
    res = client.post("/api/customer/snap-find", params={"hex_color": "NOT_A_COLOR"}, headers=customer_headers)
    assert res.status_code == 400
    assert "invalid hex color" in res.json()["detail"].lower()


def test_customer_order_request_lifecycle(client, customer_headers, dealer_headers, admin_headers):
    # 1. Customer creates request
    payload = {
        "customer_name": "Rohan Sharma",
        "customer_phone": "9876543210",
        "shade_id": 1,
        "size_preference": "4L",
        "dealer_id": 1,
    }
    res_create = client.post("/api/customer/order-request", json=payload, headers=customer_headers)
    assert res_create.status_code == 200
    req_id = res_create.json()["request_id"]
    assert req_id is not None

    # 2. Dealer retrieves assigned requests
    res_dealer = client.get("/api/dealer/1/customer-requests", headers=dealer_headers)
    assert res_dealer.status_code == 200
    requests = res_dealer.json()
    assert any(r["id"] == req_id for r in requests)

    # 3. Dealer updates request status to 'contacted'
    res_update = client.patch(
        f"/api/dealer/1/customer-requests/{req_id}",
        json={"status": "contacted"},
        headers=dealer_headers,
    )
    assert res_update.status_code == 200
    assert res_update.json()["status"] == "contacted"

    # 4. Admin oversees requests across dealerships
    res_admin = client.get("/api/admin/customer-requests", headers=admin_headers)
    assert res_admin.status_code == 200
    assert any(r["id"] == req_id and r["status"] == "contacted" for r in res_admin.json())
