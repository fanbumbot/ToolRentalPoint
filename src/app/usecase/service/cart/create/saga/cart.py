from sqlalchemy.orm import Session

from .....saga.saga_step import SagaStep

from ......domain.entity import EntityCQImpl

class CreateCartSagaStep(SagaStep):
    def __init__(
        self,
        session: Session,
        cart_impl: EntityCQImpl
    ):
        super().__init__(session, cart_impl)

    def __call__(self):
        pass