from sqlalchemy.orm import Session

from .....domain.entity import EntityCQImpl

from .....domain.discount.implementation.queries.get_discount_by_product import GetDiscountByProductQuery
from .....domain.discount.discount import Discount, DiscountValue
from .....domain.discount.discount_season import DiscountSeason, Period
from .....domain.product.product import Product
from .....domain.product.cost import Cost
from .....domain.product.rental_period import RentalPeriodDuration

from .....infrastructure.models import ProductModel, DiscountModel, DiscountPeriodModel

class GetDiscountByProductQueryImpl(GetDiscountByProductQuery):
    def __init__(
        self,
        session: Session,
        discount_impl: EntityCQImpl,
        product_impl: EntityCQImpl
    ):
        self.session = session
        self.discount_impl = discount_impl
        self.product_impl = product_impl
    
    def __call__(self, product_id):
        discount_model = self.session.query(DiscountModel).filter(
            DiscountModel.product_id == product_id
        ).one_or_none()

        if discount_model == None:
            return None
        
        discount_season_model = self.session.query(DiscountPeriodModel).filter(
            DiscountPeriodModel.id == discount_model.discount_period_id
        ).one_or_none()

        if discount_season_model == None:
            return None
        
        product_model = self.session.query(ProductModel).filter(
            ProductModel.id == product_id
        ).one_or_none()

        if product_model == None:
            return None
        
        if product_model.standard_rental_period:
            duration = RentalPeriodDuration(product_model.standard_rental_period)
        else:
            duration = None
        
        product = Product(
            product_model.id,
            self.product_impl,
            Cost(product_model.rent_or_buy_cost),
            duration
        )

        discount_season = DiscountSeason(
            discount_season_model.id,
            self.discount_impl,
            Period(discount_season_model.start, discount_season_model.end)
        )

        discount = Discount(
            discount_model.id,
            self.discount_impl,
            product,
            DiscountValue(discount_model.discount_value),
            discount_season
        )

        return discount
        
