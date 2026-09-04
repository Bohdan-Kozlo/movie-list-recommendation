"""Persistence-to-domain mappings owned by the recommendation adapter."""

from decimal import Decimal

from app.adapters.postgres.mappers.catalogue import to_title_details
from app.modules.catalog.models import CatalogueTitle
from app.modules.recommendations.domain import RatedTitle


def to_rated_title(title: CatalogueTitle, value: Decimal) -> RatedTitle:
    """Translate an ORM rating join row into the recommendation domain value."""
    return RatedTitle(title=to_title_details(title), value=float(value))
