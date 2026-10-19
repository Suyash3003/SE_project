from app.database import Document, Field


class Dealer(Document):
    __collection__ = "dealers"
    name = Field("name")
    code = Field("code")
    region_id = Field("region_id")
    warehouse_id = Field("warehouse_id")
    city = Field("city")
    state = Field("state")
    latitude = Field("latitude")
    longitude = Field("longitude")
    tier = Field("tier")
    credit_limit = Field("credit_limit")
    performance_score = Field("performance_score")


class DealerOrder(Document):
    __collection__ = "dealer_orders"
    dealer_id = Field("dealer_id")
    sku_id = Field("sku_id")
    quantity = Field("quantity")
    order_date = Field("order_date")
    status = Field("status")
    is_ai_suggested = Field("is_ai_suggested")
    order_source = Field("order_source")
    savings_amount = Field("savings_amount")
