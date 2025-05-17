from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ....domain.user_auth.user import User
from ....domain.user_auth.login import Login
from ....domain.user_auth.password import Password, HashedPassword, Crypto
from ....domain.user_auth.user import WrongPasswordError, AlreadyRegisteredError

from ....domain.wallet.wallet import Wallet, Money

from ....domain.user_auth.implementation.queries.is_registered import IsUserRegisteredQuery
from ....domain.entity import EntityCQImpl
from ....domain.user_auth.user import User
from ....infrastructure.models.user import UserModel

from passlib.context import CryptContext

from ..cart import CartService

from .create.command import UserCreateCommand

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginDoesNotExistError(Exception):
    pass

class UserService:
    def __init__(
        self,
        session: Session,
        user_impl: EntityCQImpl,
        wallet_impl: EntityCQImpl,
        cart_service: CartService
    ):
        self.session = session
        self.cart_service = cart_service
        self.user_impl = user_impl
        self.wallet_impl = wallet_impl

    def create(
        self,
        login: str,
        password: str
    ):
        now = datetime.now(timezone.utc)
        user_id = UserCreateCommand(
            self.session,
            self.user_impl,
            self.wallet_impl,
            crypt_context
        )(login, password, now)

        self.cart_service.create(user_id)

        return user_id

    def is_registered(self, login: str):
        return self.user_impl.call(IsUserRegisteredQuery, Login(login))
    
    def get_model_by_login(self, login: str):
        return self.session.query(UserModel).filter_by(login=login).one_or_none()
    
    def load_user_auth_domain(self, model: UserModel):
        user = User(
            model.id,
            self.user_impl,
            Login(model.login),
            HashedPassword(crypt_context, model.password)
        )

        return user
    
    def log_in(self, login: str, password: str):
        model = self.get_model_by_login(login)
        if model == None:
            raise LoginDoesNotExistError
        user = self.load_user_auth_domain(model)
        return user.log_in(password)
    
    def verify_hash_password(self, login: str, checked_hash_password: str) -> bool:
        model = self.get_model_by_login(login)
        return model.password == checked_hash_password
    
    def get_wallet(self, user_id):
        user_model = self.session.query(UserModel).filter(
            UserModel.id == user_id
        ).one_or_none()

        if user_model == None:
            return None

        wallet = Wallet(
            user_id,
            self.wallet_impl,
            Money(user_model.money)
        )

        return wallet
    
    def top_up_wallet(self, user_id, money_amount: int):
        wallet = self.get_wallet(user_id)
        if wallet == None:
            return None
        
        wallet.gain_money(Money(money_amount))