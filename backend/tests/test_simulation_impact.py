import pytest
from app.simulations.impact_engine import calculate_scenario_impact
from app.simulations.scenarios import get_scenario_list, get_scenario_data


def test_calculate_truck_strike_impact(db):
    res = calculate_scenario_impact(db, "TRUCK_STRIKE")
    assert res["id"] == "TRUCK_STRIKE"
    assert "West" in res["affected_regions"]
    summary = res["dashboard_summary"]
    assert "stockout_count" in summary
    assert "revenue_at_risk" in summary
    assert "avg_days_of_cover" in summary
    assert res["calculation_method"] == "dynamic_inventory_impact_engine"


def test_calculate_heatwave_impact(db):
    res = calculate_scenario_impact(db, "HEATWAVE")
    assert res["id"] == "HEATWAVE"
    assert res["demand_multiplier"] == 1.35
    assert len(res["impacted_warehouses"]) > 0


def test_simulation_endpoints_require_auth(client):
    # Unauthenticated should fail with 401
    res = client.get("/api/simulate/scenarios")
    assert res.status_code == 401

    res_data = client.get("/api/simulate/scenario/HEATWAVE/data")
    assert res_data.status_code == 401


def test_simulation_endpoints_with_admin_auth(client, admin_headers):
    res = client.get("/api/simulate/scenarios", headers=admin_headers)
    assert res.status_code == 200
    scenarios = res.json()
    assert any(s["id"] == "HEATWAVE" for s in scenarios)
