from __future__ import annotations
from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    sku_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderRequestCreate(BaseModel):
    customer_name: str = Field(..., min_length=2)
    customer_phone: str = Field(..., min_length=10)
    shade_id: int = Field(..., gt=0)
    size_preference: str = Field("4L", pattern="^(1L|4L|10L|20L)$")
    dealer_id: int = Field(..., gt=0)
    quantity: int = Field(1, ge=1, le=100)
    delivery_address: str = Field("", max_length=300)
    notes: str = Field("", max_length=500)



class CustomerOrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(requested|contacted|fulfilled|cancelled)$")
