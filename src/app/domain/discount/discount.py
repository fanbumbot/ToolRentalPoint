from typing import Union
import math

from .discount_value import DiscountValue

from ..entity import Entity, EntityCQImpl
from ..validation import type_validate

from ..product.product import Product

from .implementation.queries.get_discount_by_product import GetDiscountByProductQuery
from .implementation.queries.is_product_with_discount import IsProductWithDiscountQuery

from ..product.product import Product
from ..product.cost import Cost
from ..product.quantity import Quantity
from ..product.rental_period import RentalPeriodDuration

from .discount_season import DiscountSeason

class ProductAlreadyHasDiscount(Exception):
    pass

class Discount(Entity):
    def __init__(
        self,
        id,
        impl: EntityCQImpl,
        product: Product,
        discount_value: DiscountValue,
        discount_season: DiscountSeason
    ):
        super().__init__(id, impl)
        self.product = product
        self.discount_value = discount_value
        self.discount_season = discount_season

        impl.validate_from_domain([GetDiscountByProductQuery])

    @classmethod
    def create(
        cls,
        id,
        impl: EntityCQImpl,
        product: Product,
        discount_value: DiscountValue,
        discount_season: DiscountSeason
    ):
        type_validate(product, "Product", Product)
        type_validate(discount_value, "Discount value", DiscountValue)
        type_validate(discount_season, "Discount season", DiscountSeason)

        impl.validate_from_domain([IsProductWithDiscountQuery])
        if impl.call(IsProductWithDiscountQuery, product):
            raise ProductAlreadyHasDiscount

        discount = Discount(id, impl, product, discount_value, discount_season)
        return discount
    
    @classmethod
    def get_from_product(
        cls,
        impl: EntityCQImpl, 
        product_id
    ) -> "Discount":
        discount = impl.call(GetDiscountByProductQuery, product_id)
        return discount
    
    def get_final_cost(
        self,
        quantity: Quantity,
        current_rental_period_duration: Union[RentalPeriodDuration, None]
    ):
        product = self.product

        initial_cost = product._initial_cost
        cost_with_discount = Cost(math.floor(initial_cost.amount * (1.0 - self.discount_value.amount)))
        product._initial_cost = cost_with_discount
        cost = product.get_final_cost(quantity, current_rental_period_duration)

        product._initial_cost = initial_cost
        return cost