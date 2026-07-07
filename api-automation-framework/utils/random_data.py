"""Dynamic test data generation utilities."""

from __future__ import annotations

from faker import Faker

fake = Faker()


def user_payload() -> dict[str, str]:
    """Return a dynamic user payload."""
    return {
        "name": fake.name(),
        "job": fake.job(),
        "email": fake.unique.email(),
    }


def product_payload() -> dict[str, str | float]:
    """Return a dynamic product payload."""
    return {
        "name": fake.word().title(),
        "description": fake.sentence(nb_words=8),
        "price": round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2),
    }
