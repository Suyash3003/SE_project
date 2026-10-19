from app.database import Document, Field


class Product(Document):
    __collection__ = "products"
    name = Field("name")
    category = Field("category")
    sub_category = Field("sub_category")
    base_type = Field("base_type")
    finish = Field("finish")
    sizes_available = Field("sizes_available")
    price_per_litre = Field("price_per_litre")


class Shade(Document):
    __collection__ = "shades"
    product_id = Field("product_id")
    shade_code = Field("shade_code")
    shade_name = Field("shade_name")
    hex_color = Field("hex_color")
    rgb_r = Field("rgb_r")
    rgb_g = Field("rgb_g")
    rgb_b = Field("rgb_b")
    shade_family = Field("shade_family")
    is_trending = Field("is_trending")


class SKU(Document):
    __collection__ = "skus"
    shade_id = Field("shade_id")
    size = Field("size")
    sku_code = Field("sku_code")
    unit_cost = Field("unit_cost")
    mrp = Field("mrp")
