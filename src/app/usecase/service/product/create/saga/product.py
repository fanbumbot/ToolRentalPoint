from datetime import timedelta

from sqlalchemy.orm import Session

from .....saga.saga_step import SagaStep

from ......domain.entity import EntityCQImpl

from ......domain.product.product import Product, RentalPeriodDuration, Cost

from ......infrastructure.models import ProductModel

class ProductCostCreateSagaStep(SagaStep):
    def __init__(
        self,
        session: Session,
        product_impl: EntityCQImpl,
        product_model: ProductModel
    ):
        super().__init__(session, product_impl)
        self.product_model = product_model

    def __call__(self):
        if self.product_model.standard_rental_period:
            duration = RentalPeriodDuration(timedelta(days=self.product_model.standard_rental_period))
        else:
            duration = None

        product = Product.create(
            None,
            self.impl,
            Cost(self.product_model.rent_or_buy_cost),
            duration
        )
        return product