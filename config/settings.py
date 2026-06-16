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
SURVEY_RATE: Final[float] = 0.60  # of non-abandoned contacts
ABANDON_RATE: Final[float] = 0.15  # of all contacts
FCR_RATE: Final[float] = 0.68  # first-contact resolution rate

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

# Delivery SLA in days: zone × modality → (min_days, max_days) inclusive
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
    0.04,
    0.06,
    0.10,
    0.10,
    0.08,
    0.22,
    0.10,
    0.10,
    0.13,
    0.07,
]
MOTIVO_WEIGHTS_LATE: Final[list[float]] = [
    0.46,
    0.25,
    0.08,
    0.05,
    0.03,
    0.06,
    0.02,
    0.02,
    0.01,
    0.02,
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
    # Electrónica
    {
        "sku": "ELEC-TV55",
        "name": 'Televisor 55" 4K',
        "category": "Electrónica",
        "subcategory": "TV",
        "price": 399990.0,
    },
    {
        "sku": "ELEC-NB15",
        "name": 'Notebook 15" i7',
        "category": "Electrónica",
        "subcategory": "Computación",
        "price": 549990.0,
    },
    {
        "sku": "ELEC-SPK1",
        "name": "Parlante Bluetooth",
        "category": "Electrónica",
        "subcategory": "Audio",
        "price": 49990.0,
    },
    {
        "sku": "ELEC-TAB1",
        "name": 'Tablet 10"',
        "category": "Electrónica",
        "subcategory": "Computación",
        "price": 199990.0,
    },
    {
        "sku": "ELEC-PHN1",
        "name": "Smartphone Android",
        "category": "Electrónica",
        "subcategory": "Telefonía",
        "price": 299990.0,
    },
    # Hogar
    {
        "sku": "HOGA-LAV1",
        "name": "Lavadora 10kg",
        "category": "Hogar",
        "subcategory": "Línea Blanca",
        "price": 359990.0,
    },
    {
        "sku": "HOGA-REF1",
        "name": "Refrigerador No Frost",
        "category": "Hogar",
        "subcategory": "Línea Blanca",
        "price": 499990.0,
    },
    {
        "sku": "HOGA-MIC1",
        "name": "Microondas 25L",
        "category": "Hogar",
        "subcategory": "Electrodomésticos",
        "price": 79990.0,
    },
    {
        "sku": "HOGA-LIC1",
        "name": "Licuadora 1.5L",
        "category": "Hogar",
        "subcategory": "Electrodomésticos",
        "price": 29990.0,
    },
    # Ropa
    {
        "sku": "ROPA-CAM1",
        "name": "Camisa Hombre",
        "category": "Ropa",
        "subcategory": "Hombre",
        "price": 19990.0,
    },
    {
        "sku": "ROPA-VES1",
        "name": "Vestido Mujer",
        "category": "Ropa",
        "subcategory": "Mujer",
        "price": 24990.0,
    },
    {
        "sku": "ROPA-ZAP1",
        "name": "Zapatillas Running",
        "category": "Ropa",
        "subcategory": "Calzado",
        "price": 59990.0,
    },
    # Deporte
    {
        "sku": "DEP-BIC1",
        "name": "Bicicleta MTB",
        "category": "Deporte",
        "subcategory": "Ciclismo",
        "price": 199990.0,
    },
    {
        "sku": "DEP-GIM1",
        "name": "Set Pesas 20kg",
        "category": "Deporte",
        "subcategory": "Fitness",
        "price": 49990.0,
    },
    # Jardín
    {
        "sku": "JAR-CES1",
        "name": "Cortadora de Pasto",
        "category": "Jardín",
        "subcategory": "Herramientas",
        "price": 149990.0,
    },
]

PRODUCT_WEIGHTS: Final[list[float]] = [
    0.08,
    0.06,
    0.05,
    0.05,
    0.07,
    0.07,
    0.06,
    0.06,
    0.05,
    0.10,
    0.09,
    0.08,
    0.06,
    0.05,
    0.07,
]

# ── Customer segments ─────────────────────────────────────────────────────────
# Thresholds for nuevo/recurrente/VIP based on customer index percentile
CUSTOMER_SEGMENT_THRESHOLDS: Final[tuple[float, float]] = (0.40, 0.85)
