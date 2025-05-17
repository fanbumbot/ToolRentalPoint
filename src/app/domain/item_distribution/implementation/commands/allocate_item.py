from abc import ABC

class AllocateItemCommand(ABC):
    def __call__(self, item_id, order_id):
        pass