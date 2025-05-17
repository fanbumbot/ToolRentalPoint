from enum import Enum

class OrderStatus(Enum):
    AwaitingPayment = 0
    HasBeenPaid = 1
    HasBeenReceived = 2
    
    DeniedByEmployee = 3
    DeniedByCustomer = 4
    DeniedBySystem = 5