from datetime import timedelta

from sqlalchemy.orm import Session

from .....domain.entity import EntityCQImpl

from .....infrastructure.models import ProductModel

from .saga import ProductCreateSaga

class ProductCreateCommand:
    def __init__(
        self,
        session: Session,
        product_impl: EntityCQImpl
    ):
        self.session = session
        self.product_impl = product_impl

    def __call__(
        self,
        slug: str,
        category_id,
        name: str,
        description: str,
        image: str,
        rent_or_buy_cost: int,
        standard_rental_period: timedelta,
        is_for_rent_or_sale: bool
    ):
        product_model = ProductModel(
            slug = slug,
            category_id = category_id,
            name = name,
            description = description,
            image = image,
            rent_or_buy_cost = rent_or_buy_cost,
            standard_rental_period = standard_rental_period,
            is_active = True,
            is_for_rent_or_sale = is_for_rent_or_sale
        )

        saga = ProductCreateSaga(
            self.session,
            self.product_impl,
            product_model
        )
        saga()
        return product_model.id