from __future__ import annotations
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator

class CreateShadeSchema(BaseModel):
    shade_name: str = Field(..., min_length=2, max_length=100)
    hex_color: str = Field(..., min_length=4, max_length=9)
    shade_family: str = Field(..., min_length=2, max_length=50)
    product_id: int
    is_trending: bool = False
    initial_stock_per_warehouse: Optional[int] = Field(200, ge=0, le=50000)

    @field_validator("hex_color")
    @classmethod
    def validate_hex(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith("#"):
            v = f"#{v}"
        if len(v) not in (4, 7):
            raise ValueError("Hex color must be #RGB or #RRGGBB")
        return v.upper()

class AddStockSchema(BaseModel):
    warehouse_id: int
    sku_id: int
    quantity: int = Field(..., gt=0, le=100000)
