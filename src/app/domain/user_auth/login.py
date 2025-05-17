from dataclasses import dataclass
import re

from ..validation import type_validate

class LoginDoesNotMeetRequirementsError(Exception):
    pass

regex = "^[a-z0-9_]{3,16}$"

@dataclass(frozen=True)
class Login:
    global regex
    pattern = re.compile(regex)
    value: str

    def __post_init__(self):
        type_validate(self.value, "Login", str)
        if not re.fullmatch(self.__class__.pattern, self.value):
            raise LoginDoesNotMeetRequirementsError("Login does not meet the requirements")
        
        