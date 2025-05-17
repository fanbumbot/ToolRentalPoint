from typing import Union, Any

from ..entity import Entity, EntityCQImpl
from ..validation import type_validate

from .item_status import ItemStatus

from .implementation.commands.allocate_item import AllocateItemCommand
from .implementation.commands.deallocate_item import DeallocateItemCommand
from .implementation.commands.update_item_status import UpdateItemStatusCommand

class WrongItemStatusError(Exception):
    def __init__(self, status: ItemStatus):
        self.status = status

class ItemCannotBeRented(Exception):
    pass

class ItemCannotBeSold(Exception):
    pass

class Item(Entity):
    def __init__(
        self,
        id,
        impl: EntityCQImpl,
        can_be_sold: bool,
        can_be_rented: bool,
        status: ItemStatus,
        owner_id: Union[Any, None]
    ):
        super().__init__(id, impl)
        self.can_be_sold = can_be_sold
        self.can_be_rented = can_be_rented
        self._status = status
        self.owner_id = owner_id

        impl.validate_from_domain([
            AllocateItemCommand,
            DeallocateItemCommand,
            UpdateItemStatusCommand
        ])

    @property
    def status(self):
        return self._status

    @classmethod
    def create(
        cls,
        id,
        impl: EntityCQImpl,
        can_be_sold: bool = True,
        can_be_rented: bool = True
    ):
        type_validate(can_be_sold, "Can_be_sold argument", bool)
        type_validate(can_be_sold, "Can_be_rented argument", bool)
        return Item(id, impl, can_be_sold, can_be_rented, ItemStatus.Unknown, None)

    def __allocate(self, order_id, owner_id):
        self._status = ItemStatus.Allocated
        self.owner_id = owner_id
        self.impl.call(UpdateItemStatusCommand, self.id, self._status)
        self.impl.call(AllocateItemCommand, self.id, order_id)
    
    def allocate_for_rent(self, order_id, owner_id):
        if not self.can_be_rented:
            raise ItemCannotBeRented

        if self._status != ItemStatus.OnStock:
            raise WrongItemStatusError(self._status)

        self.__allocate(order_id, owner_id)

    def allocate_for_sale(self, order_id, owner_id):
        if not self.can_be_sold:
            raise ItemCannotBeRented

        if self._status != ItemStatus.OnStock:
            raise WrongItemStatusError(self._status)

        self.__allocate(order_id, owner_id)

    def deallocate(self):
        if self._status != ItemStatus.Allocated:
            raise WrongItemStatusError(self._status)

        self._status = ItemStatus.OnStock
        self.owner_id = None

        self.impl.call(UpdateItemStatusCommand, self.id, self._status)
        self.impl.call(DeallocateItemCommand, self.id)

    def rent(self):
        if self._status != ItemStatus.Allocated:
            raise WrongItemStatusError(self._status)
        
        if not self.can_be_rented:
            raise ItemCannotBeRented
        
        self._status = ItemStatus.Rented
        self.impl.call(UpdateItemStatusCommand, self.id, self._status)

    def sell(self):
        if self._status != ItemStatus.Allocated:
            raise WrongItemStatusError(self._status)
        
        if not self.can_be_sold:
            raise ItemCannotBeSold
        
        self._status = ItemStatus.Sold
        self.impl.call(UpdateItemStatusCommand, self.id, self._status)

    def return_rented(self):
        if self._status != ItemStatus.Rented:
            raise WrongItemStatusError(self._status)
        
        if not self.can_be_rented:
            raise ItemCannotBeRented

        self._status = ItemStatus.OnStock
        self.owner_id = None

        self.impl.call(UpdateItemStatusCommand, self.id, self._status)
        self.impl.call(DeallocateItemCommand, self.id)