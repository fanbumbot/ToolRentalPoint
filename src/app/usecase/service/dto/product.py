from datetime import datetime
from dataclasses import dataclass

@dataclass(frozen=True)
class ProductView:
    id: int
    name: str
    slug: str
    description: str
    image: str
    is_for_rent_or_sale: bool
    category: str

    old_cost: int
    new_cost: int
    discount: float

    standard_rental_period: int
    
    items_in_stock: int

@dataclass(frozen=True)
class ProductInCartView:
    id: int
    slug: str
    name: str
    image: str
    is_for_rent_or_buy: bool

    old_cost: int
    new_cost: int
    discount: float
    is_for_rent_or_sale: bool
    total_cost: int

    items_in_stock: int

@dataclass(frozen=True)
class ProductForSaleInCartView(ProductInCartView):
    quantity: int

@dataclass(frozen=True)
class ProductForRentInCartView(ProductInCartView):
    standard_duration_in_days: int
    days: int
    start_rent: datetime
    end_rent: datetime