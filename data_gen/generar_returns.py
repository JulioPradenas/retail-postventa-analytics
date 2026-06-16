"""Generator for product return records."""

from pathlib import Path

import numpy as np
import pandas as pd

from config import settings


def generate_returns(orders: pd.DataFrame, shipments: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Generate return records for ~12% of orders.

    Each order has at most one return. Return date is always after delivery.

    Args:
        orders: Output of generate_orders().
        shipments: Output of generate_shipments().
        seed: Random seed.

    Returns:
        DataFrame with return records.
    """
    rng = np.random.default_rng(seed)
    n = len(orders)

    has_return = rng.random(n) < settings.RETURN_RATE
    returning = orders[has_return].copy()
    nr = len(returning)

    ship_lookup = shipments.set_index("order_id")["actual_delivery_date"]
    delivery_dates = pd.to_datetime(returning["order_id"].map(ship_lookup).values)

    # Return date: 3-21 days after delivery
    return_offsets = rng.integers(3, 22, size=nr)
    return_dates = [
        (delivery_dates[i] + pd.Timedelta(days=int(return_offsets[i]))).date() for i in range(nr)
    ]

    motivos = settings.RETURN_MOTIVOS
    motivo_w = np.array(settings.RETURN_MOTIVO_WEIGHTS, dtype=float)
    motivo_idx = rng.choice(len(motivos), size=nr, p=motivo_w)
    selected_motivos = [motivos[int(i)] for i in motivo_idx]

    statuses = settings.RETURN_STATUS_VALUES
    status_w = np.array(settings.RETURN_STATUS_WEIGHTS, dtype=float)
    status_idx = rng.choice(len(statuses), size=nr, p=status_w)
    selected_statuses = [statuses[int(i)] for i in status_idx]

    return pd.DataFrame(
        {
            "return_id": [f"RET-{i + 1:06d}" for i in range(nr)],
            "order_id": returning["order_id"].values,
            "return_date": return_dates,
            "return_motivo": selected_motivos,
            "return_status": selected_statuses,
        }
    )


def save_returns(df: pd.DataFrame, output_dir: Path = Path("data_gen/csv")) -> Path:
    """Save returns DataFrame to CSV.

    Args:
        df: Returns DataFrame.
        output_dir: Directory to write the file.

    Returns:
        Path to the saved CSV.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "returns.csv"
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    from data_gen.generar_orders import generate_orders
    from data_gen.generar_shipments import generate_shipments

    orders_df = generate_orders()
    shipments_df = generate_shipments(orders_df)
    df = generate_returns(orders_df, shipments_df)
    p = save_returns(df)
    print(f"Generated {len(df)} returns → {p}")
    print(f"Return rate: {len(df) / len(orders_df):.1%}")
