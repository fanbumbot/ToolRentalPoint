from dataclasses import dataclass
from datetime import datetime

from ....domain.order.order_status import OrderStatus

@dataclass(frozen=True)
class OrderView:
    id: int
    total_cost: int
    status: str
    items: list["OrderProductView"]

    time_left_for_payment: int

@dataclass(frozen=True)
class OrderProductView:
    id: int
    image: str
    name: str

    is_for_rent_or_sale: bool
    start_rental_period: datetime
    end_rental_period: datetime
    quantity: int

    initial_cost: int
    cost_with_discount: int
    discount: float

    total_cost: int
    
@dataclass(frozen=True)
class OrderWithItemsView:
    id: int
    status: str
    items: list["OrderProductView"]

@dataclass(frozen=True)
class OrderItemView:
    id: int
    sticked_id: str
    image: str
    name: str
