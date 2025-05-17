from dataclasses import dataclass

@dataclass(frozen=True)
class UserCreateModel:
    login: str
    password: str