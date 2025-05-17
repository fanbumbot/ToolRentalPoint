from dataclasses import dataclass
import re

from typing import Protocol, runtime_checkable

from ..validation import type_validate

class PasswordDoesNotMeetRequirementsError(Exception):
    pass

regex = "^[a-z0-9_]{3,16}$"

@runtime_checkable
class Crypto(Protocol):
    def hash(self, string: str) -> str:
        raise NotImplementedError

    def verify(self, check_string: str, hashed_string: str):
        raise NotImplementedError

@dataclass(frozen=True)
class Password:
    global regex

    pattern = re.compile(regex)
    value: str

    def __post_init__(self):
        type_validate(self.value, "Password", str)
        if not re.fullmatch(self.__class__.pattern, self.value):
            raise PasswordDoesNotMeetRequirementsError("Login does not meet the requirements")
        
    def get_hashed(self, crypto: Crypto) -> "HashedPassword":
        return HashedPassword.create(crypto, self.value)

@dataclass(frozen=True)
class HashedPassword:
    crypto: Crypto
    hashed_password: str

    def __post_init__(self):
        type_validate(self.crypto, "Crypto interface", Crypto)
        type_validate(self.hashed_password, "Hashed password", str)

    @classmethod
    def create(cls, crypto: Crypto, password: str):
        if password == None:
            return cls(crypto, hashed_password)
        hashed_password = cls.hash(crypto, password)
        return HashedPassword(crypto, hashed_password)
    
    @classmethod
    def hash(self, crypto: Crypto, password: str) -> str:
        hashed_password = crypto.hash(password)
        return hashed_password

    def verify(self, password: str) -> bool:
        return self.crypto.verify(password, self.hashed_password)

