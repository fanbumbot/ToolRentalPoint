from dataclasses import dataclass
from typing import Union, Any

from enum import Enum

class ProductOrderBy(Enum):
    Random = 0
    Name = 1
    Cost = 2

@dataclass(frozen=True)
class ProductFilter:
    substring: str
    category_id: Union[Any, None]

    min_cost: Union[int, None]
    max_cost: Union[int, None]

    order_by: ProductOrderBy = ProductOrderBy.Random
    is_ascending: bool = True