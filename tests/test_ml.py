"""Tests for the contact prediction ML model."""

import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from ml.predict_contact import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    TARGET,
    build_pipeline,
    prepare_features,
)

SAMPLE_SIZE = 20


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    """Synthetic DataFrame mimicking fct_orders + has_contact label."""
    rng = __import__("numpy").random.default_rng(42)
    n = SAMPLE_SIZE
    is_late = rng.integers(0, 2, n)
    return pd.DataFrame(
        {
            "is_late_int": is_late,
            "delay_days": is_late * rng.integers(1, 6, n),
            "promised_delivery_days": rng.integers(2, 8, n),
            "total_amount": rng.integers(10_000, 300_000, n).astype(float),
            "quantity": rng.integers(1, 4, n),
            "carrier": rng.choice(["Chilexpress", "StarKen", "DHL"], n),
            "zone": rng.choice(["RM", "regions"], n),
            "carrier_modality": rng.choice(["express", "normal"], n),
            "customer_segment": rng.choice(["nuevo", "recurrente", "VIP"], n),
            "region": rng.choice(["RM", "Valparaíso", "Biobío"], n),
            "product_category": rng.choice(["Electrónica", "Hogar", "Ropa"], n),
            "has_contact": rng.integers(0, 2, n),
        }
    )


def test_prepare_features_shape(sample_df: pd.DataFrame) -> None:
    X, y = prepare_features(sample_df)
    assert X.shape == (SAMPLE_SIZE, len(NUMERIC_FEATURES) + len(CATEGORICAL_FEATURES))
    assert len(y) == SAMPLE_SIZE


def test_prepare_features_no_target_in_x(sample_df: pd.DataFrame) -> None:
    X, _ = prepare_features(sample_df)
    assert TARGET not in X.columns


def test_prepare_features_y_is_binary(sample_df: pd.DataFrame) -> None:
    _, y = prepare_features(sample_df)
    assert set(y.unique()).issubset({0, 1})


def test_build_pipeline_structure() -> None:
    pipeline = build_pipeline()
    assert isinstance(pipeline, Pipeline)
    assert "preprocessor" in pipeline.named_steps
    assert "classifier" in pipeline.named_steps


def test_pipeline_fit_predict(sample_df: pd.DataFrame) -> None:
    X, y = prepare_features(sample_df)
    pipeline = build_pipeline()
    pipeline.fit(X, y)
    preds = pipeline.predict(X)
    assert len(preds) == SAMPLE_SIZE
    assert set(preds).issubset({0, 1})


def test_pipeline_predict_proba_valid_range(sample_df: pd.DataFrame) -> None:
    X, y = prepare_features(sample_df)
    pipeline = build_pipeline()
    pipeline.fit(X, y)
    probas = pipeline.predict_proba(X)[:, 1]
    assert (probas >= 0).all()
    assert (probas <= 1).all()
