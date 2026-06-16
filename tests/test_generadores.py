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


# ── Shipments ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def shipments(orders: pd.DataFrame) -> pd.DataFrame:
    from data_gen.generar_shipments import generate_shipments

    return generate_shipments(orders, seed=42)


def test_shipments_one_per_order(orders: pd.DataFrame, shipments: pd.DataFrame) -> None:
    assert len(shipments) == len(orders)
    assert set(shipments["order_id"]) == set(orders["order_id"])


def test_shipments_promised_date_after_order_date(shipments: pd.DataFrame) -> None:
    order_dates = pd.to_datetime(shipments["order_date"])
    promised_dates = pd.to_datetime(shipments["promised_date"])
    assert (promised_dates >= order_dates).all()


def test_shipments_late_flag_matches_dates(shipments: pd.DataFrame) -> None:
    promised = pd.to_datetime(shipments["promised_date"])
    actual = pd.to_datetime(shipments["actual_delivery_date"])
    is_late = shipments["is_late"].astype(bool)
    assert (actual[is_late] > promised[is_late]).all()
    assert (actual[~is_late] <= promised[~is_late]).all()


def test_shipments_late_rate_in_expected_range(shipments: pd.DataFrame) -> None:
    late_rate = shipments["is_late"].mean()
    assert 0.05 < late_rate < 0.35, f"Unexpected late rate: {late_rate:.2%}"


# ── Contacts ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def contacts(orders: pd.DataFrame, shipments: pd.DataFrame) -> pd.DataFrame:
    from data_gen.generar_contacts import generate_contacts

    return generate_contacts(orders, shipments, seed=42)


def test_contacts_reference_valid_orders(orders: pd.DataFrame, contacts: pd.DataFrame) -> None:
    assert contacts["order_id"].isin(orders["order_id"]).all()


def test_contacts_date_after_delivery(shipments: pd.DataFrame, contacts: pd.DataFrame) -> None:
    merged = contacts.merge(
        shipments[["order_id", "actual_delivery_date"]], on="order_id", how="left"
    )
    contact_dates = pd.to_datetime(merged["contact_date"])
    delivery_dates = pd.to_datetime(merged["actual_delivery_date"])
    assert (contact_dates > delivery_dates).all()


def test_abandoned_contacts_have_null_metrics(contacts: pd.DataFrame) -> None:
    abandoned = contacts[contacts["is_abandoned"]]
    if len(abandoned) == 0:
        pytest.skip("No abandoned contacts in sample")
    for col in ["agent_id", "aht_seconds", "csat_score", "fcr"]:
        assert abandoned[col].isna().all(), f"Abandoned contact has non-null {col}"


def test_handled_contacts_have_metrics(contacts: pd.DataFrame) -> None:
    handled = contacts[~contacts["is_abandoned"]]
    assert len(handled) > 0
    for col in ["agent_id", "aht_seconds", "csat_score", "fcr"]:
        assert handled[col].notna().all(), f"Handled contact has null {col}"


def test_late_orders_have_higher_contact_rate(
    shipments: pd.DataFrame, contacts: pd.DataFrame
) -> None:
    contacted_orders = set(contacts["order_id"].unique())
    late_orders = set(shipments[shipments["is_late"]]["order_id"])
    ontime_orders = set(shipments[~shipments["is_late"]]["order_id"])
    late_rate = len(contacted_orders & late_orders) / max(len(late_orders), 1)
    ontime_rate = len(contacted_orders & ontime_orders) / max(len(ontime_orders), 1)
    assert late_rate > ontime_rate


# ── Returns ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def returns(orders: pd.DataFrame, shipments: pd.DataFrame) -> pd.DataFrame:
    from data_gen.generar_returns import generate_returns

    return generate_returns(orders, shipments, seed=42)


def test_returns_reference_valid_orders(orders: pd.DataFrame, returns: pd.DataFrame) -> None:
    assert returns["order_id"].isin(orders["order_id"]).all()


def test_returns_date_after_delivery(shipments: pd.DataFrame, returns: pd.DataFrame) -> None:
    merged = returns.merge(
        shipments[["order_id", "actual_delivery_date"]], on="order_id", how="left"
    )
    return_dates = pd.to_datetime(merged["return_date"])
    delivery_dates = pd.to_datetime(merged["actual_delivery_date"])
    assert (return_dates > delivery_dates).all()


def test_returns_rate_in_expected_range(orders: pd.DataFrame, returns: pd.DataFrame) -> None:
    rate = len(returns) / len(orders)
    assert 0.05 < rate < 0.25, f"Unexpected return rate: {rate:.2%}"


def test_returns_unique_order_ids(returns: pd.DataFrame) -> None:
    assert returns["order_id"].is_unique


# ── Surveys ───────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def surveys(contacts: pd.DataFrame) -> pd.DataFrame:
    from data_gen.generar_surveys import generate_surveys

    return generate_surveys(contacts, seed=42)


def test_surveys_reference_non_abandoned_contacts(
    contacts: pd.DataFrame, surveys: pd.DataFrame
) -> None:
    handled_ids = set(contacts[~contacts["is_abandoned"]]["contact_id"])
    assert surveys["contact_id"].isin(handled_ids).all()


def test_surveys_unique_contact_ids(surveys: pd.DataFrame) -> None:
    assert surveys["contact_id"].is_unique


def test_surveys_nps_in_range(surveys: pd.DataFrame) -> None:
    assert surveys["nps_score"].between(0, 10).all()


def test_surveys_satisfaction_in_range(surveys: pd.DataFrame) -> None:
    assert surveys["overall_satisfaction"].between(1, 5).all()


def test_surveys_date_after_contact(contacts: pd.DataFrame, surveys: pd.DataFrame) -> None:
    merged = surveys.merge(contacts[["contact_id", "contact_date"]], on="contact_id")
    survey_dates = pd.to_datetime(merged["survey_date"])
    contact_dates = pd.to_datetime(merged["contact_date"])
    assert (survey_dates > contact_dates).all()
