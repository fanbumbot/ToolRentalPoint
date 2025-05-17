from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .....domain.discount.implementation.queries.is_product_with_discount import IsProductWithDiscountQuery
from .....domain.discount.discount_season import DiscountSeason
from .....domain.product.product import Product

from .....infrastructure.models import DiscountModel

class IsProductWithDiscountQueryImpl(IsProductWithDiscountQuery):
    def __init__(self, session: Session):
        self.session = session

    def __call__(self, product: Product) -> bool:
        count = self.session.query(DiscountModel).filter(
            DiscountModel.product_id == product.id
        ).count()

        return count > 0