from ...usecase.service.discount import DiscountService

from ...domain.entity import EntityCQImpl

from ...usecase.implementation.discount.queries.get_discount_by_product import GetDiscountByProductQuery, GetDiscountByProductQueryImpl
from ...usecase.implementation.discount.queries.is_discount_season_belonged import IsDiscountSeasonBelongedQuery, IsDiscountSeasonBelongedQueryImpl
from ...usecase.implementation.discount.queries.is_product_with_discount import IsProductWithDiscountQuery, IsProductWithDiscountQueryImpl

def get_discount_service(session):
    discount_service = DiscountService(session)
    return discount_service