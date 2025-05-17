from sqlalchemy.orm import Session

from .....infrastructure.models import CartModel, CartAndProductModel

class ClearCartCommand:
    def __init__(self, session: Session):
        self.session = session

    def __call__(
        self,
        user_id
    ):
        cart_model = self.session.query(CartModel).filter(
            CartModel.user_id == user_id
        ).one()

        self.session.query(CartAndProductModel).filter(
            CartAndProductModel.cart_id == cart_model.id
        ).delete(synchronize_session=False)