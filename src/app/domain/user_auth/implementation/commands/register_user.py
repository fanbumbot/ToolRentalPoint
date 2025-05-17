from abc import ABC

from ...login import Login
from ...password import HashedPassword

class RegisterUserCommand(ABC):
    def __call__(
        self,
        login: Login,
        hashed_password: HashedPassword
    ):
        pass