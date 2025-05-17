from sqlalchemy.orm import Session

from ......domain.entity import EntityCQImpl

from .....saga.create_saga import CreateSaga

from ......infrastructure.models import UserModel

from .auth import UserCreateAuthSagaStep, Crypto
from .wallet import UserCreateWalletSagaStep

class UserCreateSaga(CreateSaga):
    def __init__(
        self,
        session: Session,
        user_impl: EntityCQImpl,
        wallet_impl: EntityCQImpl,
        user_model: UserModel,

        crypto: Crypto
    ):
        steps = [
            UserCreateAuthSagaStep(
                session,
                user_impl,
                user_model,
                crypto
            ),
            UserCreateWalletSagaStep(
                session,
                wallet_impl,
                user_model
            )
        ]
        super().__init__(steps, session, user_model)