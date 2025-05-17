from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import and_

from .....infrastructure.models import ProductModel, CartModel, CartAndProductModel


class AddToCartCommand:
    def __init__(self, session: Session):
        self.session = session

    def __call__(
        self,
        user_id,
        product_id,
        quantity: int,
        start_date: date,
        end_date: date
    ):
        cart_id = self.session.query(CartModel.id).filter(CartModel.user_id == user_id).one().tuple()[0]

        last_model = self.session.query(CartAndProductModel).filter(
            and_(
                CartAndProductModel.product_id == product_id,
                CartAndProductModel.start_rent == start_date,
                CartAndProductModel.end_rent == end_date
            )
        ).one_or_none()

        if last_model != None:
            last_model.quantity += quantity
            return last_model
        else:
            model = CartAndProductModel(
                cart_id = cart_id,
                product_id = product_id,
                start_rent = start_date,
                end_rent = end_date,
                quantity = quantity
            )
            self.session.add(model)
            return model