import unittest

from ..entity import EntityCQImpl

from .implementation.commands.update_wallet_money import UpdateWalletMoneyCommand
from .wallet import Wallet
from ..money.money import Money

class UpdateWalletMoneyCommandImpl(UpdateWalletMoneyCommand):
    def __init__(self, all_wallets: dict):
        self.all_wallets = all_wallets
    def __call__(self, wallet_id, new_money):
        self.all_wallets[wallet_id] = new_money

def get_test_impl(all_wallets):
    impl = EntityCQImpl({
        UpdateWalletMoneyCommand: UpdateWalletMoneyCommandImpl(all_wallets)
    })
    return impl

class TestCase(unittest.TestCase):
    all_wallets = dict()
    
    def test_create(self):
        impl = get_test_impl(self.__class__.all_wallets)
        wallet = Wallet.create(None, impl)
        self.assertNotEqual(wallet, None)

    def test_gain_money(self):
        impl = get_test_impl(self.__class__.all_wallets)
        wallet = Wallet.create(None, impl)
        wallet.gain_money(Money(100))
        wallet.gain_money(Money(1000))
        self.assertEqual(wallet.money.amount, 1100)

    def test_spend_money(self):
        impl = get_test_impl(self.__class__.all_wallets)
        wallet = Wallet.create(None, impl)
        wallet.gain_money(Money(1000))
        wallet.spend_money(Money(100))
        wallet.spend_money(Money(50))
        self.assertEqual(wallet.money.amount, 850)