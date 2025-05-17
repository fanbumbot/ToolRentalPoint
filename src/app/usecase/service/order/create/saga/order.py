from sqlalchemy.orm import Session

from ......domain.entity import EntityCQImpl

from .....saga.saga_step import SagaStep

from ......infrastructure.models import OrderModel

from ......domain.order.order import Order, Money, Wallet

class CreateOrderSagaStep(SagaStep):
    def __init__(
        self,
        session: Session,
        impl: EntityCQImpl,
        order_model: OrderModel,

        user_wallet: Wallet
    ):
        super().__init__(session, impl)
        self.order_model = order_model
        self.user_wallet = user_wallet

    def __call__(self):
        self.order_model.user_id
        order = Order.create(
            None,
            self.impl,
            Money(0),
            self.user_wallet
        )
        
        self.order_model.status = order.status.name