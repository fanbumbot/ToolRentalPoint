from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .saga import CreateOrderSaga

from .....infrastructure.models import OrderModel, CartModel, CartAndProductModel, OrderAndProductModel

from .....domain.entity import EntityCQImpl

class CreateOrderCommand:
    def __init__(
        self,
        session: Session,
        order_impl: EntityCQImpl,
        user_wallet
    ):
        self.session = session
        self.order_impl = order_impl
        self.user_wallet = user_wallet

    def __copy_items(self, order_model: OrderModel):
        cart_model = self.session.query(CartModel).filter(
            CartModel.user_id == order_model.user_id
        ).one_or_none()
        if cart_model == None:
            return
        
        cart_item_models = self.session.query(CartAndProductModel).filter(
            CartAndProductModel.cart_id == cart_model.id
        ).all()

        for cart_item_model in cart_item_models:
            order_item_model = OrderAndProductModel(
                order_id = order_model.id,
                product_id = cart_item_model.product_id,
                start_rent = cart_item_model.start_rent,
                end_rent = cart_item_model.end_rent,
                quantity = cart_item_model.quantity
            )
            self.session.add(order_item_model)
            self.session.flush([order_item_model])

    def __call__(
        self,
        user_id
    ):
        now = datetime.now(timezone.utc)

        order_model = OrderModel(
            user_id = user_id,
            registration_datetime = now
        )

        saga = CreateOrderSaga(
            self.session,
            order_model,
            self.order_impl,
            self.user_wallet
        )
        saga()
        order_id = order_model.id

        self.__copy_items(order_model)

        return order_id