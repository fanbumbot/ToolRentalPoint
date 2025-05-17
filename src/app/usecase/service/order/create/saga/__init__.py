from sqlalchemy.orm import Session

from ......infrastructure.models import OrderModel

from .....saga.create_saga import CreateSaga

from ......domain.entity import EntityCQImpl

from .order import CreateOrderSagaStep

class CreateOrderSaga(CreateSaga):
    def __init__(
        self,
        session: Session,
        order_model: OrderModel,
        order_impl: EntityCQImpl,
        user_wallet
    ):
        steps = [
            CreateOrderSagaStep(
                session,
                order_impl,
                order_model,
                user_wallet
            )
        ]
        super().__init__(steps, session, order_model)
        