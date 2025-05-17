from typing import Union

from ..entity import Entity, EntityCQImpl
from ..validation import type_validate

from ..money.money import Money

from .implementation.commands.update_wallet_money import UpdateWalletMoneyCommand

class NotEnoughMoneyError(ValueError):
    pass

class Wallet(Entity):
    def __init__(
        self,
        id,
        impl: EntityCQImpl,
        money: Money
    ):
        super().__init__(id, impl)
        self.impl.validate_from_domain([UpdateWalletMoneyCommand])

        self._money = money

    @classmethod
    def create(
        cls,
        id,
        impl: EntityCQImpl
    ):
        return Wallet(id, impl, Money(0))
    
    @property
    def money(self):
        return self._money
    
    def gain_money(self, gained_money: Money):
        type_validate(gained_money, "Money", Money)
        self._money = Money(self._money.amount + gained_money.amount)
        self.impl.call(UpdateWalletMoneyCommand, self.id, self._money)
        return self._money

    def spend_money(self, spent_money: Money):
        type_validate(spent_money, "Money", Money)

        if spent_money.amount > self._money.amount:
            raise NotEnoughMoneyError

        self._money = Money(self._money.amount - spent_money.amount)
        self.impl.call(UpdateWalletMoneyCommand, self.id, self._money)
        return self._money

    def give_money(self, wallet: "Wallet", money: Money):
        type_validate(wallet, "Wallet", Wallet)

        self.spend_money(money)
        wallet.gain_money(money)

        return money
        
