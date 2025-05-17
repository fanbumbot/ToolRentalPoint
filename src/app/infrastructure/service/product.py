from ...domain.entity import EntityCQImpl
from ...usecase.implementation.discount.queries.get_discount_by_product import GetDiscountByProductQuery, GetDiscountByProductQueryImpl
from ...usecase.implementation.discount.queries.is_discount_season_belonged import IsDiscountSeasonBelongedQuery, IsDiscountSeasonBelongedQueryImpl
from ...usecase.implementation.discount.queries.is_product_with_discount import IsProductWithDiscountQuery, IsProductWithDiscountQueryImpl

from ...usecase.service.product import ProductService
from .item import get_item_service

def get_product_service(session):
    product_impl = EntityCQImpl({
    })
    discount_impl = EntityCQImpl({
        IsDiscountSeasonBelongedQuery: IsDiscountSeasonBelongedQueryImpl(session),
        IsProductWithDiscountQuery: IsProductWithDiscountQueryImpl(session)
    })
    discount_impl.implementations[GetDiscountByProductQuery] = GetDiscountByProductQueryImpl(
        session, discount_impl, product_impl)
    
    item_service = get_item_service(session)
    
    product_service = ProductService(session, item_service, product_impl, discount_impl)

    return product_service