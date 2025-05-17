from abc import ABC

from ...period import Period

class IsDiscountSeasonBelongedQuery(ABC):
    def __call__(self, period: Period) -> bool:
        pass