"""Generator for post-contact survey records."""

from pathlib import Path

import numpy as np
import pandas as pd

from config import settings

# NPS score probability distributions (11 values for scores 0-10)
_NPS_PROBS_GOOD = [0.02, 0.02, 0.03, 0.03, 0.05, 0.05, 0.10, 0.15, 0.20, 0.20, 0.15]
_NPS_PROBS_BAD = [0.15, 0.15, 0.12, 0.10, 0.10, 0.10, 0.10, 0.08, 0.05, 0.03, 0.02]

_CSAT_PROBS_GOOD = [0.02, 0.05, 0.18, 0.40, 0.35]
_CSAT_PROBS_BAD = [0.20, 0.30, 0.28, 0.15, 0.07]


def generate_surveys(contacts: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Generate survey records for ~60% of non-abandoned contacts.

    Surveys are only sent to handled (non-abandoned) contacts.
    NPS and satisfaction are higher when FCR=True.

    Args:
        contacts: Output of generate_contacts().
        seed: Random seed.

    Returns:
        DataFrame with survey records.
    """
    rng = np.random.default_rng(seed)

    handled = contacts[~contacts["is_abandoned"]].copy()
    has_survey = rng.random(len(handled)) < settings.SURVEY_RATE
    surveyed = handled[has_survey].copy()
    ns = len(surveyed)

    contact_dates = pd.to_datetime(surveyed["contact_date"].values)
    survey_offsets = rng.integers(1, 4, size=ns)
    survey_dates = [
        (contact_dates[i] + pd.Timedelta(days=int(survey_offsets[i]))).date() for i in range(ns)
    ]

    fcr_values = surveyed["fcr"].astype(bool).values
    nps_scores = []
    satisfaction_scores = []
    nps_w_good = np.array(_NPS_PROBS_GOOD, dtype=float)
    nps_w_bad = np.array(_NPS_PROBS_BAD, dtype=float)
    csat_w_good = np.array(_CSAT_PROBS_GOOD, dtype=float)
    csat_w_bad = np.array(_CSAT_PROBS_BAD, dtype=float)

    for fcr in fcr_values:
        if fcr:
            nps_scores.append(int(rng.choice(11, p=nps_w_good)))
            satisfaction_scores.append(int(rng.choice([1, 2, 3, 4, 5], p=csat_w_good)))
        else:
            nps_scores.append(int(rng.choice(11, p=nps_w_bad)))
            satisfaction_scores.append(int(rng.choice([1, 2, 3, 4, 5], p=csat_w_bad)))

    return pd.DataFrame(
        {
            "survey_id": [f"SUR-{i + 1:07d}" for i in range(ns)],
            "contact_id": surveyed["contact_id"].values,
            "survey_date": survey_dates,
            "overall_satisfaction": satisfaction_scores,
            "nps_score": nps_scores,
        }
    )


def save_surveys(df: pd.DataFrame, output_dir: Path = Path("data_gen/csv")) -> Path:
    """Save surveys DataFrame to CSV.

    Args:
        df: Surveys DataFrame.
        output_dir: Directory to write the file.

    Returns:
        Path to the saved CSV.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "surveys.csv"
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    from data_gen.generar_contacts import generate_contacts
    from data_gen.generar_orders import generate_orders
    from data_gen.generar_shipments import generate_shipments

    orders_df = generate_orders()
    shipments_df = generate_shipments(orders_df)
    contacts_df = generate_contacts(orders_df, shipments_df)
    df = generate_surveys(contacts_df)
    p = save_surveys(df)
    print(f"Generated {len(df)} surveys → {p}")
    print(f"NPS promedio: {df['nps_score'].mean():.1f}")
