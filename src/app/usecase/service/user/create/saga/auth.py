from sqlalchemy.orm import Session

from .....saga.saga_step import SagaStep

from ......domain.user_auth.user import User, Login, Password, Crypto

from ......domain.entity import EntityCQImpl

from ......infrastructure.models import UserModel

class UserCreateAuthSagaStep(SagaStep):
    def __init__(
        self,
        session: Session,
        user_impl: EntityCQImpl,
        
        user_model: UserModel,
        crypto: Crypto
    ):
        super().__init__(session, user_impl)

        self.user_model = user_model
        self.crypto = crypto

    def __call__(self):
        user = User.create(
            None,
            self.impl,
            Login(self.user_model.login),
            Password(self.user_model.password),
            self.crypto
        )

        self.user_model.password = user.hashed_password
        return user
