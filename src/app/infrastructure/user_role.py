from fastapi import Depends, HTTPException
from fastapi.requests import Request

from .auth.session import get_current_user_id

from .models import UserModel
from .database import SessionLocal

from ..usecase.service.user.user_role import UserRole

def check_role(request: Request, roles: list[UserRole]):
    user_id = get_current_user_id(request)
    if user_id == None:
        raise HTTPException(status_code=401, detail="Вы не авторизованы")
    
    with SessionLocal() as session:
        user = session.query(UserModel).filter(
            UserModel.id == user_id
        ).one_or_none()
        if user == None or user.role not in UserRole._member_names_ or UserRole[user.role] not in roles:
            raise HTTPException(status_code=403, detail="У Вас недостаточно прав на данное действие")
        
def get_role(request: Request):
    user_id = get_current_user_id(request)
    if user_id == None:
        return None
    with SessionLocal() as session:
        user = session.query(UserModel).filter(
            UserModel.id == user_id
        ).one_or_none()

        if user == None or user.role not in UserRole._member_names_:
            return None
        
        role = UserRole[user.role]
        return role
    