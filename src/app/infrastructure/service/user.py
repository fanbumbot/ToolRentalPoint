from ...domain.entity import EntityCQImpl

from ...usecase.implementation.user_auth.queries.is_registered import IsUserRegisteredQuery, IsUserRegisteredQueryImpl

from ...usecase.implementation.wallet.commands.update_wallet_money import UpdateWalletMoneyCommand, UpdateWalletMoneyCommandImpl

from ...usecase.service.user import UserService
from ...usecase.service.cart import CartService
from ...usecase.service.product import ProductService
from ...usecase.service.order import OrderService

from .cart import get_cart_service

def get_user_service(session):
    user_impl = EntityCQImpl({
        IsUserRegisteredQuery: IsUserRegisteredQueryImpl(session)
    })
    wallet_impl = EntityCQImpl({
        UpdateWalletMoneyCommand: UpdateWalletMoneyCommandImpl(session)
    })

    user_service = UserService(
        session,
        user_impl,
        wallet_impl,
        get_cart_service(session)
    )
    return user_service