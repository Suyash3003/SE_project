from app.database import Document, Field


class CustomerOrderRequest(Document):
    __collection__ = "customer_order_requests"
    customer_name = Field("customer_name")
    customer_phone = Field("customer_phone")
    shade_id = Field("shade_id")
    size_preference = Field("size_preference")
    dealer_id = Field("dealer_id")
    quantity = Field("quantity")
    delivery_address = Field("delivery_address")
    user_id = Field("user_id")
    notes = Field("notes")
    status = Field("status")
    created_at = Field("created_at")
