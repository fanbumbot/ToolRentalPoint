from abc import ABC

from ...item_status import ItemStatus

class UpdateItemStatusCommand(ABC):
    def __call__(self, item_id, status: ItemStatus):
        pass