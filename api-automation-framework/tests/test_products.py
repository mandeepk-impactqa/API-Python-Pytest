"""Product endpoint tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from api.product_api import ProductAPI
from utils.json_utils import read_json


@pytest.mark.smoke
def test_list_products_matches_schema(product_api: ProductAPI) -> None:
    """Verify products can be listed and match the configured schema."""
    schema = read_json(Path("schemas/product_list_schema.json"))

    response = product_api.list_products(page=1)

    response.should_have_status(200).should_match_schema(schema)


@pytest.mark.regression
def test_get_product_by_id(product_api: ProductAPI) -> None:
    """Verify a single product can be fetched."""
    response = product_api.get_product(2)

    response.should_have_status(200).should_have_key("data")
