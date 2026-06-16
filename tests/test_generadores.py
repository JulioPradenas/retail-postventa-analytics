"""Tests for synthetic data generators. Uses n=200 for speed."""

import pandas as pd
import pytest

SMALL_N = 200


@pytest.fixture(scope="module")
def orders() -> pd.DataFrame:
    from data_gen.generar_orders import generate_orders

    return generate_orders(n=SMALL_N, seed=42)


def test_orders_row_count(orders: pd.DataFrame) -> None:
    assert len(orders) == SMALL_N


def test_orders_no_nulls_in_required_columns(orders: pd.DataFrame) -> None:
    required = ["order_id", "customer_id", "region", "order_date", "product_sku", "total_amount"]
    for col in required:
        assert orders[col].notna().all(), f"Column {col} has nulls"


def test_orders_unique_ids(orders: pd.DataFrame) -> None:
    assert orders["order_id"].is_unique


def test_orders_total_amount_positive(orders: pd.DataFrame) -> None:
    assert (orders["total_amount"] > 0).all()


def test_orders_date_in_2024(orders: pd.DataFrame) -> None:
    dates = pd.to_datetime(orders["order_date"])
    assert dates.min() >= pd.Timestamp("2024-01-01")
    assert dates.max() <= pd.Timestamp("2024-12-31")


def test_orders_segment_values(orders: pd.DataFrame) -> None:
    valid = {"nuevo", "recurrente", "VIP"}
    assert set(orders["customer_segment"].unique()).issubset(valid)
