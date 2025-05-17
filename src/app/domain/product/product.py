from dataclasses import dataclass
from typing import Union
import math

from .cost import Cost
from .rental_period import RentalPeriodDuration
from .quantity import Quantity

from ..validation import type_validate

from ..entity import Entity, EntityCQImpl

class Product(Entity):
    def __init__(
        self,
        id,
        impl: EntityCQImpl,
        initial_cost: Cost,
        standard_rental_period_duration: Union[RentalPeriodDuration, None]
    ):
        super().__init__(id, impl, )
        self._initial_cost = initial_cost
        self.standard_rental_period_duration = standard_rental_period_duration

    @classmethod
    def create(
        cls,
        id,
        impl: EntityCQImpl,
        initial_cost: Cost,
        standard_rental_period_duration: RentalPeriodDuration
    ):
        type_validate(initial_cost, "Cost", Cost)
        if standard_rental_period_duration != None:
            type_validate(standard_rental_period_duration, "Standard rental period duration", RentalPeriodDuration)

        product = Product(
            id,
            impl,
            initial_cost,
            standard_rental_period_duration
        )

        return product

    def get_initial_cost(self):
        return self._initial_cost

    def get_final_cost(
        self,
        quantity: Quantity,
        current_rental_period_duration: Union[RentalPeriodDuration, None]
    ):
        type_validate(quantity, "Quantity", Quantity)
        if current_rental_period_duration != None:
            type_validate(current_rental_period_duration, "Current rental period duration", RentalPeriodDuration)

        new_cost = self.get_initial_cost().amount

        is_for_rent = self.standard_rental_period_duration != None
        if is_for_rent and current_rental_period_duration != None:
            current_duration = current_rental_period_duration.duration
            standard_duration = self.standard_rental_period_duration.duration
            number_of_rents = math.ceil(current_duration / standard_duration)

            new_cost *= number_of_rents
        new_cost *= quantity.value

        return Cost(new_cost)