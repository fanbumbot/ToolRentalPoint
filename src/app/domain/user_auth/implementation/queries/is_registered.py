from ...login import Login

from abc import ABC

class IsUserRegisteredQuery(ABC):
    def __call__(self, login: Login) -> bool:
        pass