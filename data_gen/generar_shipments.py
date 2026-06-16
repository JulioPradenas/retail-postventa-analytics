"""Generator for synthetic shipment records (1 per order)."""

from pathlib import Path

import numpy as np
import pandas as pd

from config import settings


def generate_shipments(orders: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Generate one shipment per order.

    Args:
        orders: Output of generate_orders().
        seed: Random seed.

    Returns:
        DataFrame with shipment records; same length as orders.
    """
    rng = np.random.default_rng(seed)
    n = len(orders)

    carriers = settings.CARRIERS
    carrier_w = np.array(settings.CARRIER_WEIGHTS, dtype=float)
    carrier_idx = rng.choice(len(carriers), size=n, p=carrier_w)
    selected_carriers = [carriers[int(i)] for i in carrier_idx]
    modalities = [settings.CARRIER_MODALITY[c] for c in selected_carriers]
    zones = ["RM" if r == "RM" else "regions" for r in orders["region"]]

    # Promised delivery days: random within SLA range (inclusive)
    promised_days = [
        int(rng.integers(settings.DELIVERY_DAYS[z][m][0], settings.DELIVERY_DAYS[z][m][1] + 1))
        for z, m in zip(zones, modalities, strict=True)
    ]

    order_dates = pd.to_datetime(orders["order_date"])
    promised_dates = [
        (order_dates.iloc[i] + pd.Timedelta(days=promised_days[i])).date() for i in range(n)
    ]

    # Determine late flag per carrier's historical late probability
    late_probs = np.array(
        [settings.LATE_PROB_BY_CARRIER[c] for c in selected_carriers], dtype=float
    )
    is_late = rng.random(n) < late_probs

    actual_dates = []
    for i in range(n):
        base = pd.Timestamp(promised_dates[i])
        if is_late[i]:
            delay = int(rng.integers(1, 6))  # 1-5 days late
            actual_dates.append((base + pd.Timedelta(days=delay)).date())
        else:
            early = int(rng.integers(0, 2))  # 0-1 day early/on-time
            actual_dates.append((base - pd.Timedelta(days=early)).date())

    delay_days = [
        max(0, (pd.Timestamp(actual_dates[i]) - pd.Timestamp(promised_dates[i])).days)
        for i in range(n)
    ]

    return pd.DataFrame(
        {
            "shipment_id": [f"SHP-{i + 1:06d}" for i in range(n)],
            "order_id": orders["order_id"].values,
            "order_date": orders["order_date"].values,
            "carrier": selected_carriers,
            "carrier_modality": modalities,
            "zone": zones,
            "promised_delivery_days": promised_days,
            "promised_date": promised_dates,
            "actual_delivery_date": actual_dates,
            "is_late": is_late,
            "delay_days": delay_days,
            "delivery_status": ["delayed" if late else "delivered" for late in is_late],
        }
    )


def save_shipments(df: pd.DataFrame, output_dir: Path = Path("data_gen/csv")) -> Path:
    """Save shipments DataFrame to CSV.

    Args:
        df: Shipments DataFrame.
        output_dir: Directory to write the file.

    Returns:
        Path to the saved CSV.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "shipments.csv"
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    from data_gen.generar_orders import generate_orders

    orders_df = generate_orders()
    df = generate_shipments(orders_df)
    p = save_shipments(df)
    print(f"Generated {len(df)} shipments → {p}")
    print(f"Late rate: {df['is_late'].mean():.1%}")
