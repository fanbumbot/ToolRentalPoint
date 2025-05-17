from enum import Enum

class ItemStatus(Enum):
    Unknown = 0
    OnStock = 1
    Allocated = 2
    Rented = 3
    Sold = 4