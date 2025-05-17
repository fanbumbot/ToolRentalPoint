from dataclasses import dataclass

from ..validation import type_validate

@dataclass(frozen=True)
class DiscountValue:
    amount: float

    def __post_init__(self):
        type_validate(self.amount, "Discount in percent", float)
        if self.amount < 0.0 or self.amount > 1.0:
            raise ValueError("Discount in percent must be between 0.0 and 1.0")