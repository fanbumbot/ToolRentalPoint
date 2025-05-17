from sqlalchemy.orm import Session
from sqlalchemy import and_

from .....infrastructure.models import CartModel, CartAndProductModel

class ItemDoesNotExist(Exception):
    pass

class CartDoesNotContainThisItem(Exception):
    pass

class RemoveFromCartCommand:
    def __init__(self, session: Session):
        self.session = session

    def __call__(
        self,
        user_id,
        cart_item_id
    ):
        cart_id = self.session.query(
            CartModel.id
        ).filter(
            CartModel.user_id == user_id
        ).one().tuple()[0]

        item_id = self.session.query(CartAndProductModel).filter(
            and_(
                CartAndProductModel.cart_id == cart_id,
                CartAndProductModel.id == cart_item_id
            )
        ).one_or_none()

        if item_id == None:
            raise CartDoesNotContainThisItem

        model = self.session.query(CartAndProductModel).filter(
            CartAndProductModel.id == cart_item_id
        ).one_or_none()

        if model == None:
            raise ItemDoesNotExist
        self.session.delete(model)

        return model