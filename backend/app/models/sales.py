from app.database import Document, Field


class SalesHistory(Document):
    __collection__ = "sales_history"
    sku_id = Field("sku_id")
    region_id = Field("region_id")
    date = Field("date")
    quantity_sold = Field("quantity_sold")
    revenue = Field("revenue")
    channel = Field("channel")
