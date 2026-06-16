# Module 1: Generadores de Datos Sintéticos — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate five coherent synthetic CSV files (orders, shipments, contacts, returns, surveys) that encode the core business insight: late shipments (OTD < 90%) generate ~2.5× more contacts than on-time ones.

**Architecture:** Each generator is a standalone Python module with a `generate_*(...)  -> pd.DataFrame` function (testable without file I/O) and a `save_*(df, output_dir) -> Path` function. Generators run in dependency order: orders → shipments → contacts / returns → surveys. Business catalogs live exclusively in `config/settings.py`.

**Tech Stack:** Python 3.11+, numpy (random generation), pandas (DataFrame + CSV), uv for deps.

---

## File Map

| File | Responsibility |
|---|---|
| `config/__init__.py` | Makes config a package |
| `config/settings.py` | All catalogs, rates, constants — single source of truth |
| `data_gen/__init__.py` | Makes data_gen a package |
| `data_gen/generar_orders.py` | 10 000 synthetic orders |
| `data_gen/generar_shipments.py` | 1 shipment per order, ~15% late |
| `data_gen/generar_contacts.py` | ~35% CPO; P(contact\|late)=0.70 vs 0.27 |
| `data_gen/generar_returns.py` | ~12% of orders, post-delivery |
| `data_gen/generar_surveys.py` | ~60% of non-abandoned contacts |
| `tests/test_settings.py` | Validates catalog structure and constants |
| `tests/test_generadores.py` | Validates row counts, nulls, coherence rules |

---

### Task 1: Add runtime dependencies + config/settings.py

**Files:**
- Create: `config/__init__.py`
- Create: `config/settings.py`
- Create: `tests/test_settings.py`

- [ ] **Step 1: Add runtime dependencies**

```bash
uv add pandas numpy
```

Expected: uv resolves packages, updates uv.lock. No errors.

- [ ] **Step 2: Write failing tests for settings**

Create `tests/test_settings.py`:

```python
import pytest
from config import settings


def test_regions_and_cities_not_empty() -> None:
    for region, cities in settings.REGIONS.items():
        assert len(cities) > 0, f"Region {region} has no cities"


def test_region_weights_match_regions() -> None:
    assert len(settings.REGION_WEIGHTS) == len(settings.REGIONS)


def test_region_weights_sum_to_one() -> None:
    assert abs(sum(settings.REGION_WEIGHTS) - 1.0) < 1e-6


def test_channel_weights_sum_to_one() -> None:
    assert abs(sum(settings.CHANNEL_WEIGHTS) - 1.0) < 1e-6


def test_carrier_weights_sum_to_one() -> None:
    assert abs(sum(settings.CARRIER_WEIGHTS) - 1.0) < 1e-6


def test_product_weights_sum_to_one() -> None:
    assert abs(sum(settings.PRODUCT_WEIGHTS) - 1.0) < 1e-6


def test_products_have_required_fields() -> None:
    required = {"sku", "name", "category", "subcategory", "price"}
    for prod in settings.PRODUCTS:
        assert required.issubset(prod.keys())


def test_contact_late_prob_greater_than_on_time() -> None:
    assert settings.CONTACT_PROB_LATE > settings.CONTACT_PROB_ON_TIME


def test_n_orders_positive() -> None:
    assert settings.N_ORDERS > 0


def test_motivo_weights_match_motivos() -> None:
    assert len(settings.MOTIVO_WEIGHTS_ON_TIME) == len(settings.CONTACT_MOTIVOS)
    assert len(settings.MOTIVO_WEIGHTS_LATE) == len(settings.CONTACT_MOTIVOS)
```

- [ ] **Step 3: Run tests — expect ImportError (module doesn't exist yet)**

```bash
uv run pytest tests/test_settings.py -v
```

Expected: `ERROR` — `ModuleNotFoundError: No module named 'config'`

- [ ] **Step 4: Create `config/__init__.py`**

Create empty file at `config/__init__.py`.

- [ ] **Step 5: Create `config/settings.py`**

```python
"""Business domain catalogs and volume constants. Single source of truth."""

from typing import Final, TypedDict


class Product(TypedDict):
    """Catalog entry for a product."""

    sku: str
    name: str
    category: str
    subcategory: str
    price: float


# ── Date range ───────────────────────────────────────────────────────────────
START_DATE: Final[str] = "2024-01-01"
END_DATE: Final[str] = "2024-12-31"

# ── Volume constants ─────────────────────────────────────────────────────────
N_ORDERS: Final[int] = 10_000
N_CUSTOMERS: Final[int] = 3_000

# P(contact | on-time shipment) and P(contact | late shipment)
# Weighted avg ≈ 0.85*0.27 + 0.15*0.70 = 0.335 → CPO ~0.35
CONTACT_PROB_ON_TIME: Final[float] = 0.27
CONTACT_PROB_LATE: Final[float] = 0.70

RETURN_RATE: Final[float] = 0.12
SURVEY_RATE: Final[float] = 0.60   # of non-abandoned contacts
ABANDON_RATE: Final[float] = 0.15  # of all contacts
FCR_RATE: Final[float] = 0.68      # first-contact resolution rate

# ── Regions ──────────────────────────────────────────────────────────────────
REGIONS: Final[dict[str, list[str]]] = {
    "RM": ["Santiago", "Maipú", "Pudahuel", "La Florida", "Peñalolén", "Quilicura"],
    "Valparaíso": ["Valparaíso", "Viña del Mar", "Quilpué", "Villa Alemana"],
    "Biobío": ["Concepción", "Talcahuano", "Chillán", "Los Ángeles"],
    "Maule": ["Talca", "Curicó", "Linares"],
    "La Araucanía": ["Temuco", "Angol", "Villarrica"],
    "Los Lagos": ["Puerto Montt", "Osorno", "Castro"],
    "Antofagasta": ["Antofagasta", "Calama"],
    "Coquimbo": ["La Serena", "Coquimbo"],
}

REGION_WEIGHTS: Final[list[float]] = [0.45, 0.15, 0.12, 0.08, 0.08, 0.06, 0.03, 0.03]

# ── Carriers ─────────────────────────────────────────────────────────────────
CARRIERS: Final[list[str]] = [
    "Chilexpress",
    "StarKen",
    "DHL",
    "Correos de Chile",
    "Bluexpress",
]

CARRIER_WEIGHTS: Final[list[float]] = [0.40, 0.25, 0.15, 0.12, 0.08]

CARRIER_MODALITY: Final[dict[str, str]] = {
    "Chilexpress": "express",
    "StarKen": "normal",
    "DHL": "express",
    "Correos de Chile": "normal",
    "Bluexpress": "express",
}

# Late probability per carrier (drives OTD variation across carriers)
LATE_PROB_BY_CARRIER: Final[dict[str, float]] = {
    "Chilexpress": 0.10,
    "StarKen": 0.22,
    "DHL": 0.07,
    "Correos de Chile": 0.24,
    "Bluexpress": 0.12,
}

# Delivery SLA in days: zone × modality → (min_days, max_days)
DELIVERY_DAYS: Final[dict[str, dict[str, tuple[int, int]]]] = {
    "RM": {"express": (1, 2), "normal": (3, 5)},
    "regions": {"express": (2, 4), "normal": (5, 8)},
}

# ── Contact channels ──────────────────────────────────────────────────────────
CONTACT_CHANNELS: Final[list[str]] = ["Voz", "Chat", "App", "Correo"]
CHANNEL_WEIGHTS: Final[list[float]] = [0.45, 0.30, 0.15, 0.10]

# AHT in seconds per channel (min, max); Correo = 0 (async, not timed)
AHT_RANGE: Final[dict[str, tuple[int, int]]] = {
    "Voz": (180, 720),
    "Chat": (120, 480),
    "App": (60, 300),
    "Correo": (0, 0),
}

# ── Contact motives ───────────────────────────────────────────────────────────
CONTACT_MOTIVOS: Final[list[str]] = [
    "Despacho tardío",
    "Producto no llegó",
    "Producto dañado",
    "Producto incorrecto",
    "Cambio de dirección",
    "Consulta estado pedido",
    "Devolución voluntaria",
    "Error en cobro",
    "Consulta de garantía",
    "Otro",
]

# Motivo weights shift dramatically for late vs on-time orders
MOTIVO_WEIGHTS_ON_TIME: Final[list[float]] = [
    0.04, 0.06, 0.10, 0.10, 0.08, 0.22, 0.10, 0.10, 0.13, 0.07
]
MOTIVO_WEIGHTS_LATE: Final[list[float]] = [
    0.46, 0.25, 0.08, 0.05, 0.03, 0.06, 0.02, 0.02, 0.01, 0.02
]

# ── Return motives ────────────────────────────────────────────────────────────
RETURN_MOTIVOS: Final[list[str]] = [
    "Producto dañado",
    "Producto incorrecto",
    "No cumple expectativas",
    "Cambio de opinión",
    "Error en el pedido",
    "Talla/tamaño incorrecto",
]

RETURN_MOTIVO_WEIGHTS: Final[list[float]] = [0.25, 0.20, 0.20, 0.15, 0.12, 0.08]

RETURN_STATUS_VALUES: Final[list[str]] = ["procesada", "pendiente", "rechazada"]
RETURN_STATUS_WEIGHTS: Final[list[float]] = [0.70, 0.20, 0.10]

# ── Products ──────────────────────────────────────────────────────────────────
PRODUCTS: Final[list[Product]] = [
    {"sku": "ELEC-TV55", "name": 'Televisor 55" 4K', "category": "Electrónica", "subcategory": "TV", "price": 399990.0},
    {"sku": "ELEC-NB15", "name": 'Notebook 15" i7', "category": "Electrónica", "subcategory": "Computación", "price": 549990.0},
    {"sku": "ELEC-SPK1", "name": "Parlante Bluetooth", "category": "Electrónica", "subcategory": "Audio", "price": 49990.0},
    {"sku": "ELEC-TAB1", "name": 'Tablet 10"', "category": "Electrónica", "subcategory": "Computación", "price": 199990.0},
    {"sku": "ELEC-PHN1", "name": "Smartphone Android", "category": "Electrónica", "subcategory": "Telefonía", "price": 299990.0},
    {"sku": "HOGA-LAV1", "name": "Lavadora 10kg", "category": "Hogar", "subcategory": "Línea Blanca", "price": 359990.0},
    {"sku": "HOGA-REF1", "name": "Refrigerador No Frost", "category": "Hogar", "subcategory": "Línea Blanca", "price": 499990.0},
    {"sku": "HOGA-MIC1", "name": "Microondas 25L", "category": "Hogar", "subcategory": "Electrodomésticos", "price": 79990.0},
    {"sku": "HOGA-LIC1", "name": "Licuadora 1.5L", "category": "Hogar", "subcategory": "Electrodomésticos", "price": 29990.0},
    {"sku": "ROPA-CAM1", "name": "Camisa Hombre", "category": "Ropa", "subcategory": "Hombre", "price": 19990.0},
    {"sku": "ROPA-VES1", "name": "Vestido Mujer", "category": "Ropa", "subcategory": "Mujer", "price": 24990.0},
    {"sku": "ROPA-ZAP1", "name": "Zapatillas Running", "category": "Ropa", "subcategory": "Calzado", "price": 59990.0},
    {"sku": "DEP-BIC1", "name": "Bicicleta MTB", "category": "Deporte", "subcategory": "Ciclismo", "price": 199990.0},
    {"sku": "DEP-GIM1", "name": "Set Pesas 20kg", "category": "Deporte", "subcategory": "Fitness", "price": 49990.0},
    {"sku": "JAR-CES1", "name": "Cortadora de Pasto", "category": "Jardín", "subcategory": "Herramientas", "price": 149990.0},
]

PRODUCT_WEIGHTS: Final[list[float]] = [
    0.08, 0.06, 0.05, 0.05, 0.07,
    0.07, 0.06, 0.06, 0.05,
    0.10, 0.09, 0.08,
    0.06, 0.05,
    0.07,
]

# ── Customer segments ─────────────────────────────────────────────────────────
# Derived from customer index in pool: 0-39% nuevo, 40-84% recurrente, 85-99% VIP
CUSTOMER_SEGMENT_THRESHOLDS: Final[tuple[float, float]] = (0.40, 0.85)
```

- [ ] **Step 6: Run tests — expect all pass**

```bash
uv run pytest tests/test_settings.py -v
```

Expected: `10 passed`

- [ ] **Step 7: Run quality checks**

```bash
uv run ruff check . && uv run mypy .
```

Expected: `All checks passed!` and `Success: no issues found`

- [ ] **Step 8: Commit**

```bash
git add config/ tests/test_settings.py pyproject.toml uv.lock
git commit -m "feat: M1 — config/settings.py con catálogos de negocio"
```

---

### Task 2: generar_orders.py

**Files:**
- Create: `data_gen/__init__.py`
- Create: `data_gen/generar_orders.py`
- Modify: `tests/test_generadores.py` (add orders tests)

- [ ] **Step 1: Write failing tests for orders**

Create `tests/test_generadores.py`:

```python
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
```

- [ ] **Step 2: Run — expect ImportError**

```bash
uv run pytest tests/test_generadores.py -v
```

Expected: `ERROR — ModuleNotFoundError: No module named 'data_gen'`

- [ ] **Step 3: Create `data_gen/__init__.py`**

Create empty file at `data_gen/__init__.py`.

- [ ] **Step 4: Create `data_gen/generar_orders.py`**

```python
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
```

- [ ] **Step 5: Run tests — expect all pass**

```bash
uv run pytest tests/test_generadores.py -v
```

Expected: `6 passed`

- [ ] **Step 6: Quality checks**

```bash
uv run ruff check . && uv run mypy .
```

Expected: all clean.

- [ ] **Step 7: Commit**

```bash
git add data_gen/ tests/test_generadores.py
git commit -m "feat: M1 — generar_orders.py"
```

---

### Task 3: generar_shipments.py

**Files:**
- Create: `data_gen/generar_shipments.py`
- Modify: `tests/test_generadores.py` (add shipments tests)

- [ ] **Step 1: Add shipments tests to `tests/test_generadores.py`**

Append to the file (after the orders tests):

```python
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
```

- [ ] **Step 2: Run — expect ImportError on shipments**

```bash
uv run pytest tests/test_generadores.py -v
```

Expected: orders tests pass, shipments fixture fails with `ImportError`.

- [ ] **Step 3: Create `data_gen/generar_shipments.py`**

```python
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

    promised_days = [
        int(rng.integers(*settings.DELIVERY_DAYS[z][m]))
        for z, m in zip(zones, modalities)
    ]

    order_dates = pd.to_datetime(orders["order_date"])
    promised_dates = [
        (order_dates.iloc[i] + pd.Timedelta(days=promised_days[i])).date()
        for i in range(n)
    ]

    # Determine late flag per carrier's late probability
    late_probs = np.array(
        [settings.LATE_PROB_BY_CARRIER[c] for c in selected_carriers], dtype=float
    )
    is_late = rng.random(n) < late_probs

    # Actual delivery date
    actual_dates = []
    for i in range(n):
        base = pd.Timestamp(promised_dates[i])
        if is_late[i]:
            delay = int(rng.integers(1, 6))  # 1-5 days late
            actual_dates.append((base + pd.Timedelta(days=delay)).date())
        else:
            early = int(rng.integers(0, 2))  # 0-1 day early
            actual_dates.append((base - pd.Timedelta(days=early)).date())

    delay_days = [
        max(
            0,
            (pd.Timestamp(actual_dates[i]) - pd.Timestamp(promised_dates[i])).days,
        )
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
            "delivery_status": [
                "delayed" if late else "delivered" for late in is_late
            ],
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
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/test_generadores.py -v
```

Expected: `10 passed`

- [ ] **Step 5: Quality checks**

```bash
uv run ruff check . && uv run mypy .
```

Expected: all clean.

- [ ] **Step 6: Commit**

```bash
git add data_gen/generar_shipments.py tests/test_generadores.py
git commit -m "feat: M1 — generar_shipments.py"
```

---

### Task 4: generar_contacts.py

**Files:**
- Create: `data_gen/generar_contacts.py`
- Modify: `tests/test_generadores.py` (add contacts tests)

- [ ] **Step 1: Add contacts tests**

Append to `tests/test_generadores.py`:

```python
@pytest.fixture(scope="module")
def contacts(orders: pd.DataFrame, shipments: pd.DataFrame) -> pd.DataFrame:
    from data_gen.generar_contacts import generate_contacts

    return generate_contacts(orders, shipments, seed=42)


def test_contacts_reference_valid_orders(
    orders: pd.DataFrame, contacts: pd.DataFrame
) -> None:
    assert contacts["order_id"].isin(orders["order_id"]).all()


def test_contacts_date_after_delivery(
    shipments: pd.DataFrame, contacts: pd.DataFrame
) -> None:
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
    late_contact_rate = len(contacted_orders & late_orders) / max(len(late_orders), 1)
    ontime_contact_rate = len(contacted_orders & ontime_orders) / max(len(ontime_orders), 1)
    assert late_contact_rate > ontime_contact_rate
```

- [ ] **Step 2: Run — expect ImportError on contacts**

```bash
uv run pytest tests/test_generadores.py::test_contacts_reference_valid_orders -v
```

Expected: `ImportError: No module named 'data_gen.generar_contacts'`

- [ ] **Step 3: Create `data_gen/generar_contacts.py`**

```python
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
                "contact_id", "order_id", "contact_date", "contact_channel",
                "contact_motivo", "is_abandoned", "agent_id", "aht_seconds",
                "csat_score", "fcr",
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
        (delivery_dates[i] + pd.Timedelta(days=int(contact_offsets[i]))).date()
        for i in range(n)
    ]

    is_abandoned = rng.random(n) < settings.ABANDON_RATE

    # Metrics: null for abandoned, populated for handled
    agent_ids: list[str | None] = []
    aht_seconds: list[int | None] = []
    csat_scores: list[int | None] = []
    fcr_values: list[bool | None] = []

    for i in range(n):
        if is_abandoned[i]:
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
            # CSAT: higher when FCR, lower when not
            if fcr:
                csat_scores.append(int(rng.choice([3, 4, 5], p=[0.20, 0.40, 0.40])))
            else:
                csat_scores.append(int(rng.choice([1, 2, 3], p=[0.30, 0.40, 0.30])))

    contact_ids = [f"CON-{i + 1:07d}" for i in range(n)]

    return pd.DataFrame(
        {
            "contact_id": contact_ids,
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
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/test_generadores.py -v
```

Expected: `15 passed`

- [ ] **Step 5: Quality checks**

```bash
uv run ruff check . && uv run mypy .
```

Expected: all clean.

- [ ] **Step 6: Commit**

```bash
git add data_gen/generar_contacts.py tests/test_generadores.py
git commit -m "feat: M1 — generar_contacts.py con reglas de coherencia"
```

---

### Task 5: generar_returns.py

**Files:**
- Create: `data_gen/generar_returns.py`
- Modify: `tests/test_generadores.py` (add returns tests)

- [ ] **Step 1: Add returns tests**

Append to `tests/test_generadores.py`:

```python
@pytest.fixture(scope="module")
def returns(orders: pd.DataFrame, shipments: pd.DataFrame) -> pd.DataFrame:
    from data_gen.generar_returns import generate_returns

    return generate_returns(orders, shipments, seed=42)


def test_returns_reference_valid_orders(
    orders: pd.DataFrame, returns: pd.DataFrame
) -> None:
    assert returns["order_id"].isin(orders["order_id"]).all()


def test_returns_date_after_delivery(
    shipments: pd.DataFrame, returns: pd.DataFrame
) -> None:
    merged = returns.merge(
        shipments[["order_id", "actual_delivery_date"]], on="order_id", how="left"
    )
    return_dates = pd.to_datetime(merged["return_date"])
    delivery_dates = pd.to_datetime(merged["actual_delivery_date"])
    assert (return_dates > delivery_dates).all()


def test_returns_rate_in_expected_range(
    orders: pd.DataFrame, returns: pd.DataFrame
) -> None:
    rate = len(returns) / len(orders)
    assert 0.05 < rate < 0.25, f"Unexpected return rate: {rate:.2%}"


def test_returns_unique_order_ids(returns: pd.DataFrame) -> None:
    assert returns["order_id"].is_unique
```

- [ ] **Step 2: Run — expect ImportError**

```bash
uv run pytest tests/test_generadores.py::test_returns_reference_valid_orders -v
```

Expected: `ImportError: No module named 'data_gen.generar_returns'`

- [ ] **Step 3: Create `data_gen/generar_returns.py`**

```python
"""Generator for product return records."""

from pathlib import Path

import numpy as np
import pandas as pd

from config import settings


def generate_returns(
    orders: pd.DataFrame, shipments: pd.DataFrame, seed: int = 42
) -> pd.DataFrame:
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
    delivery_dates = pd.to_datetime(
        returning["order_id"].map(ship_lookup).values
    )

    # Return date: 3-21 days after delivery
    return_offsets = rng.integers(3, 22, size=nr)
    return_dates = [
        (delivery_dates[i] + pd.Timedelta(days=int(return_offsets[i]))).date()
        for i in range(nr)
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
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/test_generadores.py -v
```

Expected: `19 passed`

- [ ] **Step 5: Quality checks + commit**

```bash
uv run ruff check . && uv run mypy .
git add data_gen/generar_returns.py tests/test_generadores.py
git commit -m "feat: M1 — generar_returns.py"
```

---

### Task 6: generar_surveys.py

**Files:**
- Create: `data_gen/generar_surveys.py`
- Modify: `tests/test_generadores.py` (add surveys tests)

- [ ] **Step 1: Add surveys tests**

Append to `tests/test_generadores.py`:

```python
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


def test_surveys_date_after_contact(
    contacts: pd.DataFrame, surveys: pd.DataFrame
) -> None:
    merged = surveys.merge(contacts[["contact_id", "contact_date"]], on="contact_id")
    survey_dates = pd.to_datetime(merged["survey_date"])
    contact_dates = pd.to_datetime(merged["contact_date"])
    assert (survey_dates > contact_dates).all()
```

- [ ] **Step 2: Run — expect ImportError**

```bash
uv run pytest tests/test_generadores.py::test_surveys_reference_non_abandoned_contacts -v
```

Expected: `ImportError: No module named 'data_gen.generar_surveys'`

- [ ] **Step 3: Create `data_gen/generar_surveys.py`**

```python
"""Generator for post-contact survey records."""

from pathlib import Path

import numpy as np
import pandas as pd

from config import settings


def generate_surveys(contacts: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Generate survey records for ~60% of non-abandoned contacts.

    Surveys are only sent to contacts that were not abandoned (is_abandoned=False).
    Survey date is 1-3 days after contact date.

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
        (contact_dates[i] + pd.Timedelta(days=int(survey_offsets[i]))).date()
        for i in range(ns)
    ]

    # NPS: 0-10; higher for FCR=True
    fcr_values = surveyed["fcr"].astype(bool).values
    nps_scores = []
    satisfaction_scores = []
    for fcr in fcr_values:
        if fcr:
            nps_scores.append(int(rng.choice(range(11), p=[0.02, 0.02, 0.03, 0.03, 0.05, 0.05, 0.10, 0.15, 0.20, 0.20, 0.15])))
            satisfaction_scores.append(int(rng.choice([1, 2, 3, 4, 5], p=[0.02, 0.05, 0.18, 0.40, 0.35])))
        else:
            nps_scores.append(int(rng.choice(range(11), p=[0.15, 0.15, 0.12, 0.10, 0.10, 0.10, 0.10, 0.08, 0.05, 0.03, 0.02])))
            satisfaction_scores.append(int(rng.choice([1, 2, 3, 4, 5], p=[0.20, 0.30, 0.28, 0.15, 0.07])))

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
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/test_generadores.py -v
```

Expected: `24 passed`

- [ ] **Step 5: Quality checks + commit**

```bash
uv run ruff check . && uv run mypy .
git add data_gen/generar_surveys.py tests/test_generadores.py
git commit -m "feat: M1 — generar_surveys.py"
```

---

### Task 7: Integration smoke test + full CSV generation

**Files:**
- No new files — this task runs the full pipeline end-to-end.

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest -v
```

Expected: `tests/test_setup.py: 1 passed`, `tests/test_settings.py: 10 passed`, `tests/test_generadores.py: 24 passed` — `35 passed` total.

- [ ] **Step 2: Generate all 5 CSVs**

```bash
uv run python data_gen/generar_orders.py
uv run python data_gen/generar_shipments.py
uv run python data_gen/generar_contacts.py
uv run python data_gen/generar_returns.py
uv run python data_gen/generar_surveys.py
```

Expected output (approximate):
```
Generated 10000 orders → data_gen/csv/orders.csv
Generated 10000 shipments → data_gen/csv/shipments.csv  Late rate: ~15%
Generated ~3400 contacts → data_gen/csv/contacts.csv    CPO: ~0.34
Generated ~1200 returns → data_gen/csv/returns.csv      Return rate: ~12%
Generated ~1200 surveys → data_gen/csv/surveys.csv
```

- [ ] **Step 3: Verify CSV files exist and have expected row counts**

```bash
uv run python -c "
import pandas as pd
from pathlib import Path

files = {
    'orders': (9000, 11000),
    'shipments': (9000, 11000),
    'contacts': (2500, 4500),
    'returns': (800, 1600),
    'surveys': (700, 2000),
}
for name, (lo, hi) in files.items():
    df = pd.read_csv(Path('data_gen/csv') / f'{name}.csv')
    status = 'OK' if lo <= len(df) <= hi else 'WARN'
    print(f'{status}  {name}: {len(df)} rows')
"
```

Expected: all lines show `OK`.

- [ ] **Step 4: Final quality check + commit**

```bash
uv run ruff check . && uv run mypy . && uv run pytest
git add data_gen/ config/ tests/
git commit -m "feat: M1 — pipeline completo de generadores sintéticos"
```

Note: `data_gen/csv/` is in `.gitignore` — the generated CSVs are NOT committed. Only the generator code is versioned.

---

## Self-Review

**Spec coverage (PROJECT_PLAN.md §5):**
- `orders.csv` ~10 000 rows ✓ Task 2
- `shipments.csv` ~10 000 rows ✓ Task 3
- `contacts.csv` ~3 500 rows ✓ Task 4
- `returns.csv` ~1 200 rows ✓ Task 5
- `surveys.csv` ~2 000 rows ✓ Task 6
- Coherence: contact_date > delivery_date ✓ Task 4 (test + implementation)
- Coherence: late → higher P(contact) ✓ Task 4
- Coherence: abandoned → NULL metrics ✓ Task 4
- Coherence: return requires shipment ✓ Task 5
- Coherence: surveys only non-abandoned ✓ Task 6
- Catalogs in `config/settings.py` only ✓ Task 1

**Gaps:** None. All spec requirements covered.
