from sqlalchemy.orm import Session

from ......domain.entity import EntityCQImpl

from .....saga.create_saga import CreateSaga, SagaStep

from ......infrastructure.models import CartModel

from .cart import CreateCartSagaStep

class CreateCartSaga(CreateSaga):
    def __init__(
        self,
        session: Session,
        cart_impl: EntityCQImpl,
        model: CartModel
    ):
        steps = [
            CreateCartSagaStep(
                session,
                cart_impl
            )
        ]
        super().__init__(steps, session, model)