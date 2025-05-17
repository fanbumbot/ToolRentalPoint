from sqlalchemy.orm import Session

from .....saga.saga_step import SagaStep

from ......domain.wallet.wallet import Wallet

from ......domain.entity import EntityCQImpl

from ......infrastructure.models import UserModel

class UserCreateWalletSagaStep(SagaStep):
    def __init__(
        self,
        session: Session,
        wallet_impl: EntityCQImpl,
        user_model: UserModel
    ):
        super().__init__(session, wallet_impl)
        self.user_model = user_model

    def __call__(self):
        wallet = Wallet.create(None, self.impl)
        self.user_model.money = wallet.money.amount
        return wallet