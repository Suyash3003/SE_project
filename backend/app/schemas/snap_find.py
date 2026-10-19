from __future__ import annotations
import re
from pydantic import BaseModel, Field, field_validator


class SnapFindRequest(BaseModel):
    hex_color: str = Field("#FFD700", description="Hexadecimal color string")

    @field_validator("hex_color")
    @classmethod
    def validate_hex(cls, v: str) -> str:
        clean = v.strip()
        if not clean.startswith("#"):
            clean = f"#{clean}"
        if not re.match(r"^#[0-9a-fA-F]{6}$", clean):
            raise ValueError("Invalid hex color format. Expected format: #RRGGBB (e.g. #FFD700)")
        return clean.upper()
