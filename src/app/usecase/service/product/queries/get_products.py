from datetime import datetime, timezone
from typing import Union

from sqlalchemy import Integer
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from .....infrastructure.models import ProductModel, DiscountModel, DiscountPeriodModel

from ..product_filter import ProductFilter, ProductOrderBy

class GetProductsQuery:
    def __call__(
        self,
        session: Session,
        page: int,
        page_size: int = None,
        filter: ProductFilter = None
    ):
        now_datetime = datetime.now(timezone.utc)

        DiscountAlias = session.query(
            DiscountModel.product_id.label("product_id"),
            DiscountModel.discount_value.label("discount_value")
        ).join(
            DiscountPeriodModel,
            and_(
                DiscountModel.discount_period_id == DiscountPeriodModel.id,
                DiscountPeriodModel.start <= now_datetime,
                DiscountPeriodModel.end >= now_datetime
            )
        ).subquery()

        cost_with_discount = (
            func.cast(func.floor(ProductModel.rent_or_buy_cost *
            (1 - func.coalesce(DiscountAlias.c.discount_value, 0.0))), Integer)
        )

        query = session.query(
            ProductModel,
            func.coalesce(DiscountAlias.c.discount_value, 0.0).label("discount_value"),
            cost_with_discount.label("new_cost")
        ).outerjoin(
            DiscountAlias,
            ProductModel.id == DiscountAlias.c.product_id
        ).where(
            and_(
                ProductModel.is_active == True,
                ProductModel.name.ilike(f"%{filter.substring.strip()}%")
            )
        )

        min_cost = filter.min_cost
        max_cost = filter.max_cost

        if min_cost != None:
            query = query.filter(
                cost_with_discount >= min_cost
            )

        if max_cost != None:
            query = query.filter(
                cost_with_discount <= max_cost
            )

        if filter.category_id != None:
            query = query.filter(
                ProductModel.category_id == filter.category_id
            )

        if filter.order_by == ProductOrderBy.Cost:
            if filter.is_ascending:
                query = query.order_by(cost_with_discount)
            else:
                query = query.order_by(cost_with_discount.desc())
        elif filter.order_by == ProductOrderBy.Name:
            if filter.is_ascending:
                query = query.order_by(ProductModel.name)
            else:
                query = query.order_by(ProductModel.name.desc())

        total_count = query.count()

        if page_size != None:
            offset = (page - 1) * page_size
            results = query.offset(offset).limit(page_size).all()
        else:
            results = query.all()

        return results, total_count