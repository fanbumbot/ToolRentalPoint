from sqlalchemy.orm import Session

from .....infrastructure.models import ProductModel, CartModel, CartAndProductModel

class GetCartProductsQuery:
    def __init__(self, session: Session):
        self.session = session

    def __call__(self, user_id):
        cart_id = self.session.query(
            CartModel.id
        ).filter(
            CartModel.user_id == user_id
        ).one().tuple()[0]
        
        models = self.session.query(
            ProductModel, CartAndProductModel
        ).select_from(
            ProductModel
        ).filter(
            CartAndProductModel.cart_id == cart_id
        ).join(
            CartAndProductModel,
            CartAndProductModel.product_id == ProductModel.id
        ).all()

        return models
