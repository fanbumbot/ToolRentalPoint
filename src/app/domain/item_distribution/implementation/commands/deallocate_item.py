from abc import ABC

class DeallocateItemCommand(ABC):
    def __call__(self, item_id):
        pass