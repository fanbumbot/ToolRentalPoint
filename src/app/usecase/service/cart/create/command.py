from datetime import timedelta

from sqlalchemy.orm import Session

from .....domain.entity import EntityCQImpl

from .....infrastructure.models import CartModel

from .saga import CreateCartSaga

class CartCreateCommand:
    def __init__(
        self,
        session: Session,
        cart_impl: EntityCQImpl
    ):
        self.session = session
        self.cart_impl = cart_impl

    def __call__(
        self,
        user_id
    ):
        cart_model = CartModel(
            user_id = user_id
        )

        saga = CreateCartSaga(
            self.session,
            self.cart_impl,
            cart_model
        )
        saga()
        return cart_model.id