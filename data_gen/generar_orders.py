"""Generator for synthetic e-commerce orders."""

from pathlib import Path

import numpy as np
import pandas as pd

from config import settings


def generate_orders(n: int = settings.N_ORDERS, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic e-commerce orders.

    Args:
        n: Number of orders to generate.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with order records sorted by order_date.
    """
    rng = np.random.default_rng(seed)

    regions = list(settings.REGIONS.keys())
    region_w = np.array(settings.REGION_WEIGHTS, dtype=float)
    region_idx = rng.choice(len(regions), size=n, p=region_w)
    selected_regions = [regions[int(i)] for i in region_idx]
    selected_cities = [
        settings.REGIONS[r][int(rng.integers(0, len(settings.REGIONS[r])))]
        for r in selected_regions
    ]

    product_w = np.array(settings.PRODUCT_WEIGHTS, dtype=float)
    product_idx = rng.choice(len(settings.PRODUCTS), size=n, p=product_w)

    n_customers = settings.N_CUSTOMERS
    cust_w = np.ones(n_customers, dtype=float)
    vip_start = int(n_customers * settings.CUSTOMER_SEGMENT_THRESHOLDS[1])
    cust_w[vip_start:] = 3.0
    cust_w /= cust_w.sum()
    cust_idx = rng.choice(n_customers, size=n, p=cust_w)

    date_range = pd.date_range(settings.START_DATE, settings.END_DATE, freq="D")
    date_idx = rng.integers(0, len(date_range), size=n)
    order_dates = [date_range[int(i)].date() for i in date_idx]

    quantities = rng.integers(1, 4, size=n)
    lo, hi = settings.CUSTOMER_SEGMENT_THRESHOLDS

    records = []
    for i in range(n):
        prod = settings.PRODUCTS[int(product_idx[i])]
        ci = int(cust_idx[i])
        pct = ci / n_customers
        if pct < lo:
            segment = "nuevo"
        elif pct < hi:
            segment = "recurrente"
        else:
            segment = "VIP"
        qty = int(quantities[i])
        records.append(
            {
                "order_id": f"ORD-{i + 1:06d}",
                "customer_id": f"CUST-{ci + 1:05d}",
                "customer_segment": segment,
                "region": selected_regions[i],
                "city": selected_cities[i],
                "order_date": order_dates[i],
                "product_sku": prod["sku"],
                "product_name": prod["name"],
                "product_category": prod["category"],
                "product_subcategory": prod["subcategory"],
                "quantity": qty,
                "unit_price": prod["price"],
                "total_amount": prod["price"] * qty,
            }
        )

    return pd.DataFrame(records).sort_values("order_date").reset_index(drop=True)


def save_orders(df: pd.DataFrame, output_dir: Path = Path("data_gen/csv")) -> Path:
    """Save orders DataFrame to CSV.

    Args:
        df: Orders DataFrame.
        output_dir: Directory to write the file.

    Returns:
        Path to the saved CSV.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "orders.csv"
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    df = generate_orders()
    p = save_orders(df)
    print(f"Generated {len(df)} orders → {p}")
