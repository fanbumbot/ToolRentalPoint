from datetime import datetime
from dataclasses import dataclass

@dataclass(frozen=True)
class ProductInCartView:
    id: int
    image: str
    name: str
    is_for_rent_or_sale: bool
    start_rental_period: datetime
    end_rental_period: datetime
    quantity: int

    initial_cost: int
    discount: float
    cost_with_discount: int

    total_cost: int
