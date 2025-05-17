from sqlalchemy.orm import Session

from .....domain.wallet.implementation.commands.update_wallet_money import UpdateWalletMoneyCommand

from .....domain.wallet.wallet import Money

from .....infrastructure.models import UserModel

class UpdateWalletMoneyCommandImpl(UpdateWalletMoneyCommand):
    def __init__(
        self,
        session: Session
    ):
        self.session = session
    
    def __call__(
        self,
        wallet_id,
        new_money: Money
    ):
        user_model = self.session.query(UserModel).filter(
            UserModel.id == wallet_id
        ).one_or_none()

        if user_model == None:
            return
        
        user_model.money = new_money.amount