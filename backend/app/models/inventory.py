from app.database import Document, Field


class Region(Document):
    __collection__ = "regions"
    name = Field("name")
    states = Field("states")


class Warehouse(Document):
    __collection__ = "warehouses"
    name = Field("name")
    code = Field("code")
    region_id = Field("region_id")
    city = Field("city")
    state = Field("state")
    latitude = Field("latitude")
    longitude = Field("longitude")
    capacity_litres = Field("capacity_litres")


class InventoryLevel(Document):
    __collection__ = "inventory_levels"
    warehouse_id = Field("warehouse_id")
    sku_id = Field("sku_id")
    current_stock = Field("current_stock")
    reorder_point = Field("reorder_point")
    max_capacity = Field("max_capacity")
    last_updated = Field("last_updated")
    days_of_cover = Field("days_of_cover")


class InventoryTransfer(Document):
    __collection__ = "inventory_transfers"
    from_warehouse_id = Field("from_warehouse_id")
    to_warehouse_id = Field("to_warehouse_id")
    sku_id = Field("sku_id")
    quantity = Field("quantity")
    status = Field("status")
    recommended_at = Field("recommended_at")
    reason = Field("reason")
