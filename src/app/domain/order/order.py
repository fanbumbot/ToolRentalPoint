from ..entity import Entity, EntityCQImpl
from ..validation import type_validate

from .order_status import OrderStatus
from ..wallet.wallet import Wallet
from ..money.money import Money

from .implementation.commands.update_order_status import UpdateOrderStatusCommand

class WrongCurrentStatusOrderError(Exception):
    def __init__(self, status: OrderStatus):
        self.status = status

class Order(Entity):
    def __init__(
        self,
        id,
        impl: EntityCQImpl,
        status: OrderStatus,
        total_cost: Money,
        target_wallet: Wallet
    ):
        super().__init__(id, impl)
        
        impl.validate_from_domain([UpdateOrderStatusCommand])

        self._status = status
        self._total_cost = total_cost
        self._target_wallet = target_wallet

    @classmethod
    def create(
        cls,
        id,
        impl: EntityCQImpl,
        total_cost: Money,
        target_wallet: Wallet
    ):
        type_validate(total_cost, "Total cost", Money)
        type_validate(target_wallet, "Target wallet", Wallet)

        order = Order(id, impl, OrderStatus.AwaitingPayment, total_cost, target_wallet)
        return order
    
    @property
    def total_cost(self):
        return self._total_cost
    
    @property
    def status(self):
        return self._status
    
    def __set_new_status(self, status: OrderStatus):
        self.impl.call(UpdateOrderStatusCommand, self.id, status)
        self._status = status
    
    def pay(self):
        if self._status != OrderStatus.AwaitingPayment:
            raise WrongCurrentStatusOrderError(self._status)

        self._target_wallet.spend_money(self.total_cost)
        self.__set_new_status(OrderStatus.HasBeenPaid)

    def refund(self):
        if self._status == OrderStatus.HasBeenPaid:
            self._target_wallet.gain_money(self.total_cost)

    def deny_by_system(self):
        if self._status not in [
            OrderStatus.AwaitingPayment, OrderStatus.HasBeenPaid
        ]:
            raise WrongCurrentStatusOrderError(self._status)
        self.refund()
        self.__set_new_status(OrderStatus.DeniedBySystem)

    def deny_by_customer(self):
        if self._status not in [
            OrderStatus.AwaitingPayment, OrderStatus.HasBeenPaid
        ]:
            raise WrongCurrentStatusOrderError(self._status)
        self.refund()
        self.__set_new_status(OrderStatus.DeniedByCustomer)

    def deny_by_employee(self):
        if self._status not in [
            OrderStatus.AwaitingPayment, OrderStatus.HasBeenPaid
        ]:
            raise WrongCurrentStatusOrderError(self._status)
        self.refund()
        self.__set_new_status(OrderStatus.DeniedByEmployee)

    def transfer_items(self):
        if self._status != OrderStatus.HasBeenPaid:
            raise WrongCurrentStatusOrderError(self._status)
        self.__set_new_status(OrderStatus.HasBeenReceived)

    def return_item(self, item_id):
        pass
