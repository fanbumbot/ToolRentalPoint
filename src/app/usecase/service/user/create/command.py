from datetime import datetime

from sqlalchemy.orm import Session

from .....domain.entity import EntityCQImpl

from .....infrastructure.models import UserModel

from .saga import UserCreateSaga

class UserCreateCommand:
    def __init__(
        self,
        session: Session,
        user_impl: EntityCQImpl,
        wallet_impl: EntityCQImpl,
        crypt_context
    ):
        self.session = session
        self.user_impl = user_impl
        self.wallet_impl = wallet_impl
        self.crypt = crypt_context

    def __call__(
        self,
        login: str,
        password: str,
        now: datetime
    ):
        user_model = UserModel(
            login = login,
            password = password,
            registration_datetime = now,
            last_login_datetime = now,
            role = "Common",
            blocked = False,
            money = 0
        )

        saga = UserCreateSaga(
            self.session,
            self.user_impl,
            self.wallet_impl,
            user_model,
            self.crypt
        )
        saga()

        return user_model.id