from abc import ABC

from ...order_status import OrderStatus

class UpdateOrderStatusCommand(ABC):
    def __call__(self, order_id, status: OrderStatus):
        pass