
from ..entity import Entity, EntityCQImpl
from ..validation import type_validate

from .login import Login
from .password import HashedPassword, Password, Crypto

from .implementation.commands.register_user import RegisterUserCommand
from .implementation.queries.is_registered import IsUserRegisteredQuery

class AlreadyRegisteredError(Exception):
    pass

class WrongPasswordError(Exception):
    pass

class User(Entity):
    def __init__(
        self,
        id,
        impl: EntityCQImpl,
        login: Login,
        hashed_password: HashedPassword
    ):
        super().__init__(id, impl)

        self.login = login
        self.hashed_password = hashed_password

        self.impl = impl

    @classmethod
    def create(
        cls,
        id,
        impl: EntityCQImpl,
        login: Login,
        password: Password,
        crypto: Crypto
    ):
        type_validate(login, "Login", Login)
        type_validate(password, "Password", Password)
        type_validate(crypto, "Crypto", Crypto)

        impl.validate_from_domain([
            IsUserRegisteredQuery,
        ])

        if impl.call(IsUserRegisteredQuery, login):
            raise AlreadyRegisteredError(f"Account with login {login} has already been registered")

        hashed_password = password.get_hashed(crypto)

        user = User(id, impl, login, hashed_password)

        return user
    
    def log_in(self, password: str) -> bool:
        if not self.hashed_password.verify(password):
            raise WrongPasswordError


    