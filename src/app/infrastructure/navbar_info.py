from dataclasses import dataclass

from sqlalchemy.orm import Session

from fastapi import Request
from fastapi.responses import RedirectResponse

from .auth.session import get_current_user_id, TokenTimeOutError

from .service.user import get_user_service
from .user_role import get_role

@dataclass(frozen=True)
class NavbarInfo:
    user_id: int
    money: int
    role: str

def get_navbar_info(request: Request, session: Session):
    try:
        user_id = get_current_user_id(request)
    except:
        return None
    if user_id == None:
        return None
    service = get_user_service(session)

    money = service.get_wallet(user_id).money.amount

    role = get_role(request)
    role = role.name if role else None

    return NavbarInfo(user_id, money, role)
