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
