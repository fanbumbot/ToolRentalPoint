from ...usecase.service.order import OrderService

from ...domain.entity import EntityCQImpl

from ...usecase.implementation.order.commands.update_order_status_command import UpdateOrderStatusCommand, UpdateOrderStatusCommandImpl

from .user import get_user_service
from .product import get_product_service
from .item import get_item_service

def get_order_service(session):
    order_impl = EntityCQImpl({
        UpdateOrderStatusCommand: UpdateOrderStatusCommandImpl(session)
    })
    user_service = get_user_service(session)
    product_service = get_product_service(session)
    item_service = get_item_service(session)

    order_service = OrderService(session, order_impl, user_service, product_service, item_service)
    return order_service