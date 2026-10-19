from __future__ import annotations
"""
Train Prophet models for top SKU-region combinations.
Models are saved as .pkl files for instant loading at startup.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pickle
from pathlib import Path
from app.database import SessionLocal
from app.models import SalesHistory, SKU, Shade
from app.config import MODEL_DIR


def train_all_models():
    """Train Prophet models for all available SKU-region sales data."""
    try:
        from prophet import Prophet
        import pandas as pd
    except ImportError:
        print("  Prophet not installed. Skipping training.")
        return

    db = SessionLocal()
    model_dir = Path(MODEL_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)

    sales_by_combo = {}
    for sale in db.query(SalesHistory).all():
        key = (sale.sku_id, sale.region_id)
        sales_by_combo.setdefault(key, []).append(sale)
    combos = [
        (sku_id, region_id, len(sales))
        for (sku_id, region_id), sales in sales_by_combo.items()
        if len(sales) > 100
    ]

    print(f"  Found {len(combos)} SKU-region combinations with sufficient data.")
    trained = 0

    for combo in combos:
        sku_id, region_id, count = combo

        # Get sales data
        sales = sorted(
            sales_by_combo[(sku_id, region_id)],
            key=lambda sale: sale.date,
        )

        if len(sales) < 100:
            continue

        df = pd.DataFrame([
            {"ds": s.date, "y": s.quantity_sold}
            for s in sales
        ])

        try:
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,
            )
            model.add_country_holidays(country_name="IN")
            model.fit(df)

            filepath = model_dir / f"prophet_{sku_id}_{region_id}.pkl"
            with open(filepath, "wb") as f:
                pickle.dump(model, f)

            sku = db.query(SKU).filter(SKU.id == sku_id).first()
            shade = db.query(Shade).filter(Shade.id == sku.shade_id).first() if sku else None
            name = shade.shade_name if shade else f"SKU-{sku_id}"
            print(f"  Trained: {name} (Region {region_id}) - {count} records")
            trained += 1

        except Exception as e:
            print(f"  Warning: Failed to train model for SKU {sku_id}, Region {region_id}: {e}")

    db.close()
    print(f"\n  Successfully trained {trained} Prophet models.")


if __name__ == "__main__":
    train_all_models()
