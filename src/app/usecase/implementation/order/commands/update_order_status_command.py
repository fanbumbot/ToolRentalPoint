from sqlalchemy.orm import Session

from .....domain.order.implementation.commands.update_order_status import UpdateOrderStatusCommand

from .....domain.order.order_status import OrderStatus

from .....infrastructure.models import OrderModel

class UpdateOrderStatusCommandImpl(UpdateOrderStatusCommand):
    def __init__(self, session: Session):
        self.session = session

    def __call__(
        self,
        order_id,
        status: OrderStatus
    ):
        order_model = self.session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).one_or_none()

        if order_model == None:
            return
        
        order_model.status = status.name