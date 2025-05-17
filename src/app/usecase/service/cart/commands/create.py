from sqlalchemy.orm import Session

from .....infrastructure.models import CartModel

class CreateCartCommand:
    def __init__(self, session: Session):
        self.session = session

    def __call__(self, user_id):
        cart_model = CartModel(user_id=user_id)
        self.session.add(cart_model)
        return cart_model.id