"""Generator for post-sale contact records."""

from pathlib import Path

import numpy as np
import pandas as pd

from config import settings


def generate_contacts(
    orders: pd.DataFrame, shipments: pd.DataFrame, seed: int = 42
) -> pd.DataFrame:
    """Generate contact records for orders that trigger post-sale contact.

    Contact probability: CONTACT_PROB_LATE for late shipments, else CONTACT_PROB_ON_TIME.
    Abandoned contacts have null agent_id, aht_seconds, csat_score, fcr.

    Args:
        orders: Output of generate_orders().
        shipments: Output of generate_shipments().
        seed: Random seed.

    Returns:
        DataFrame with one row per contact event.
    """
    rng = np.random.default_rng(seed)

    merged = orders.merge(shipments[["order_id", "actual_delivery_date", "is_late"]], on="order_id")

    is_late = merged["is_late"].astype(bool).values
    contact_probs = np.where(is_late, settings.CONTACT_PROB_LATE, settings.CONTACT_PROB_ON_TIME)
    has_contact = rng.random(len(merged)) < contact_probs
    contacting = merged[has_contact].copy()

    n = len(contacting)
    if n == 0:
        return pd.DataFrame(
            columns=[
                "contact_id",
                "order_id",
                "contact_date",
                "contact_channel",
                "contact_motivo",
                "is_abandoned",
                "agent_id",
                "aht_seconds",
                "csat_score",
                "fcr",
            ]
        )

    channels = settings.CONTACT_CHANNELS
    channel_w = np.array(settings.CHANNEL_WEIGHTS, dtype=float)
    channel_idx = rng.choice(len(channels), size=n, p=channel_w)
    selected_channels = [channels[int(i)] for i in channel_idx]

    motivos = settings.CONTACT_MOTIVOS
    is_late_contacting = contacting["is_late"].astype(bool).values
    selected_motivos = []
    for late in is_late_contacting:
        w = np.array(
            settings.MOTIVO_WEIGHTS_LATE if late else settings.MOTIVO_WEIGHTS_ON_TIME,
            dtype=float,
        )
        selected_motivos.append(motivos[int(rng.choice(len(motivos), p=w))])

    # Contact date: 1-7 days after actual delivery
    delivery_dates = pd.to_datetime(contacting["actual_delivery_date"].values)
    contact_offsets = rng.integers(1, 8, size=n)
    contact_dates = [
        (delivery_dates[i] + pd.Timedelta(days=int(contact_offsets[i]))).date() for i in range(n)
    ]

    is_abandoned = rng.random(n) < settings.ABANDON_RATE

    agent_ids: list[str | None] = []
    aht_seconds: list[int | None] = []
    csat_scores: list[int | None] = []
    fcr_values: list[bool | None] = []

    for i in range(n):
        if bool(is_abandoned[i]):
            agent_ids.append(None)
            aht_seconds.append(None)
            csat_scores.append(None)
            fcr_values.append(None)
        else:
            agent_ids.append(f"AGT-{int(rng.integers(1, 51)):03d}")
            ch = selected_channels[i]
            lo, hi = settings.AHT_RANGE[ch]
            aht = int(rng.integers(lo, hi + 1)) if hi > 0 else 0
            aht_seconds.append(aht)
            fcr = bool(rng.random() < settings.FCR_RATE)
            fcr_values.append(fcr)
            if fcr:
                csat_scores.append(int(rng.choice([3, 4, 5], p=[0.20, 0.40, 0.40])))
            else:
                csat_scores.append(int(rng.choice([1, 2, 3], p=[0.30, 0.40, 0.30])))

    return pd.DataFrame(
        {
            "contact_id": [f"CON-{i + 1:07d}" for i in range(n)],
            "order_id": contacting["order_id"].values,
            "contact_date": contact_dates,
            "contact_channel": selected_channels,
            "contact_motivo": selected_motivos,
            "is_abandoned": is_abandoned,
            "agent_id": agent_ids,
            "aht_seconds": aht_seconds,
            "csat_score": csat_scores,
            "fcr": fcr_values,
        }
    )


def save_contacts(df: pd.DataFrame, output_dir: Path = Path("data_gen/csv")) -> Path:
    """Save contacts DataFrame to CSV.

    Args:
        df: Contacts DataFrame.
        output_dir: Directory to write the file.

    Returns:
        Path to the saved CSV.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "contacts.csv"
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    from data_gen.generar_orders import generate_orders
    from data_gen.generar_shipments import generate_shipments

    orders_df = generate_orders()
    shipments_df = generate_shipments(orders_df)
    df = generate_contacts(orders_df, shipments_df)
    p = save_contacts(df)
    print(f"Generated {len(df)} contacts → {p}")
    print(f"CPO: {len(df) / len(orders_df):.3f}")
    print(f"Abandon rate: {df['is_abandoned'].mean():.1%}")
