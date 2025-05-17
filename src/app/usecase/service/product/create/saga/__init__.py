from sqlalchemy.orm import Session

from ......domain.entity import EntityCQImpl

from .....saga.create_saga import CreateSaga

from ......infrastructure.models import ProductModel

from .product import ProductCostCreateSagaStep

class ProductCreateSaga(CreateSaga):
    def __init__(
        self,
        session: Session,
        product_impl: EntityCQImpl,
        product_model: ProductModel
    ):
        steps = [
            ProductCostCreateSagaStep(
                session,
                product_impl,
                product_model
            )
        ]
        super().__init__(steps, session, product_model)