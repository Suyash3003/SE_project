import pytest
from app.services.copilot_service import _sanitize_widget, _heuristic_response
from app.services.forecast_service import _generate_fallback_forecast


def test_forecast_endpoint_requires_auth(client):
    res = client.get("/api/forecast/10?region_id=4&horizon=30")
    assert res.status_code == 401


def test_forecast_endpoint_with_auth(client, admin_headers):
    res = client.get("/api/forecast/10?region_id=4&horizon=30", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["sku_id"] == 10
    assert "forecast" in data
    assert "annotations" in data


def test_copilot_endpoint_requires_auth(client):
    res = client.post("/api/copilot/chat", json={"message": "Any stockouts in Pune?"})
    assert res.status_code == 401


def test_copilot_heuristic_fallback():
    res = _heuristic_response("Critical bridal red in pune", "NORMAL")
    assert "text" in res
    assert "ui_widget" in res
    assert res["ui_widget"]["type"] == "TRANSFER_CARD"
    assert res["ui_widget"]["props"]["to"] == "Pune"


def test_copilot_widget_sanitizer():
    valid = {"type": "TRANSFER_CARD", "props": {"from": "Mumbai", "to": "Pune", "qty": 100}}
    sanitized = _sanitize_widget(valid)
    assert sanitized["type"] == "TRANSFER_CARD"
    assert sanitized["props"]["qty"] == 100

    invalid_type = {"type": "EXECUTE_ARBITRARY_SQL", "props": {"query": "DROP TABLE users;"}}
    assert _sanitize_widget(invalid_type) is None

    non_dict = "not a dict"
    assert _sanitize_widget(non_dict) is None
