from abc import ABC

from ....money.money import Money

class UpdateWalletMoneyCommand(ABC):
    def __call__(self, wallet_id, new_money: Money):
        pass