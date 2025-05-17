from dataclasses import dataclass

from ..validation import type_validate

class QuantityIsNotPositiveError(ValueError):
    pass

@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self):
        type_validate(self.value, "Quantity value", int)

        if self.value <= 0:
            raise QuantityIsNotPositiveError