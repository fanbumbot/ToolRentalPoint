from ...usecase.service.cart import CartService

from .product import get_product_service

def get_cart_service(session):
    product_service = get_product_service(session)
    cart_service = CartService(session, product_service)

    return cart_service