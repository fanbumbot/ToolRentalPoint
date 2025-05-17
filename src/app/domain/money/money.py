from dataclasses import dataclass

from ..validation import type_validate

class MoneyAmountIsNotPositive(Exception):
    pass

@dataclass(frozen=True)
class Money:
    amount: int

    def __post_init__(self):
        type_validate(self.amount, "Money amount", int)

        if self.amount < 0:
            raise MoneyAmountIsNotPositive